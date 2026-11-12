"""Functional and code-generation checks for the hardware store comparison."""

from pathlib import Path
import random
import shutil
import struct
import subprocess
import tempfile
import unittest

from unicorn import Uc, UC_ARCH_ARM64, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn import UC_MEM_READ, UC_MODE_ARM
from unicorn import arm64_const as regs

EXAMPLE = (
    Path(__file__).resolve().parents[2] / "examples/naive/aarch64/vector_store_compare"
)


class VectorStoreCompareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        clang = shutil.which("clang-19")
        objcopy = shutil.which("llvm-objcopy-19")
        nm = shutil.which("llvm-nm-19")
        if not all((clang, objcopy, nm)):
            raise unittest.SkipTest("AArch64 compiler and LLVM object tools required")
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.builds = {}
        compilers = {"clang": [clang, "--target=aarch64-none-elf"]}
        gcc = shutil.which("aarch64-linux-gnu-gcc")
        if gcc:
            compilers["gcc"] = [gcc]
        for name, command in compilers.items():
            obj = Path(cls.directory.name) / f"{name}.o"
            binary = obj.with_suffix(".bin")
            subprocess.run(
                command
                + [
                    "-O3",
                    "-std=gnu11",
                    "-march=armv8-a",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-c",
                    str(EXAMPLE / "vector_abs_store_kernels.c"),
                    "-o",
                    str(obj),
                ],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                [objcopy, "-O", "binary", "--only-section=.text", obj, binary],
                check=True,
                capture_output=True,
            )
            symbols = {}
            for line in subprocess.check_output(
                [nm, "-S", obj], text=True
            ).splitlines():
                fields = line.split()
                if len(fields) == 4 and fields[3].startswith("vector_abs_"):
                    symbols[fields[3]] = (int(fields[0], 16), int(fields[1], 16))
            cls.builds[name] = (binary.read_bytes(), symbols)

    def test_only_store_encoding_changes(self):
        for compiler, (code, symbols) in self.builds.items():
            with self.subTest(compiler=compiler):
                functions = []
                for name in ("vector_abs_st1", "vector_abs_str"):
                    offset, size = symbols[name]
                    self.assertEqual(offset % 64, 0)
                    functions.append(
                        struct.unpack(f"<{size // 4}I", code[offset : offset + size])
                    )
                self.assertEqual(len(functions[0]), len(functions[1]))
                changes = 0
                first_store = None
                for index, (st1, store) in enumerate(zip(*functions)):
                    if st1 == store:
                        continue
                    changes += 1
                    if first_store is None:
                        first_store = index * 4
                    # Register fields are identical; only ST1/STR opcodes differ.
                    self.assertEqual(st1 & ~0x3FF, 0x4C9F7800)
                    self.assertEqual(store & ~0x3FF, 0x3C810400)
                    self.assertEqual(st1 & 0x3FF, store & 0x3FF)
                self.assertEqual(changes, 32)  # 16 kernel stores + 16 drain stores
                self.assertEqual(first_store % 64, 60)

    def check_execution(self, code, entry, blocks, offset):
        emu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
        code_base, stop = 0x100000, 0x10F000
        stack_base, stack_top = 0x400000, 0x40FFF0
        src, dst = 0x210000 + offset, 0x310000 + offset
        for base in (code_base, 0x200000, 0x300000, stack_base):
            emu.mem_map(base, 0x20000)
        emu.mem_write(code_base, code)
        emu.reg_write(regs.UC_ARM64_REG_CPACR_EL1, 3 << 20)
        emu.reg_write(regs.UC_ARM64_REG_SP, stack_top)
        preserved = {}
        for number in range(19, 30):
            reg = getattr(regs, f"UC_ARM64_REG_X{number}")
            preserved[reg] = 0x12340000 + number
        for number in range(8, 16):
            reg = getattr(regs, f"UC_ARM64_REG_Q{number}")
            preserved[reg] = 0xABCD00000000 + number
        for reg, value in preserved.items():
            emu.reg_write(reg, value)

        words = max(blocks, 2) * 64
        rng = random.Random(20261110)
        data = [rng.getrandbits(32) for _ in range(words)]
        data[:8] = [
            0,
            0x80000000,
            0x3F800000,
            0xBF800000,
            0x7F800000,
            0xFF800000,
            0xFFC12345,
            0x80000001,
        ]
        packed = struct.pack(f"<{words}I", *data)
        guard = b"\xa5" * 64
        poison = b"\x5a" * len(packed)
        emu.mem_write(src - 64, guard + packed + guard)
        emu.mem_write(dst - 64, guard + poison + guard)
        accesses = [0, 0]

        def memory_access(uc, access, address, size, value, user_data):
            if stack_base <= address and address + size <= stack_base + 0x20000:
                return
            self.assertGreaterEqual(blocks, 2, "Small count must not access buffers")
            read = access == UC_MEM_READ
            base = src if read else dst
            self.assertGreaterEqual(address, base)
            self.assertLessEqual(address + size, base + len(packed))
            accesses[0 if read else 1] += size

        emu.hook_add(UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE, memory_access)
        # A second call must reinitialize all pipeline state and local pointers.
        for invocation in range(2):
            emu.mem_write(dst, poison)
            accesses[:] = [0, 0]
            emu.reg_write(regs.UC_ARM64_REG_X0, dst)
            emu.reg_write(regs.UC_ARM64_REG_X1, src)
            emu.reg_write(regs.UC_ARM64_REG_X2, blocks)
            emu.reg_write(regs.UC_ARM64_REG_X30, stop)
            emu.emu_start(code_base + entry, stop, count=max(1000, blocks * 100))
            self.assertEqual(emu.reg_read(regs.UC_ARM64_REG_PC), stop)
            expected = (
                struct.pack(f"<{words}I", *(word & 0x7FFFFFFF for word in data))
                if blocks >= 2
                else poison
            )
            self.assertEqual(bytes(emu.mem_read(dst, len(packed))), expected)
            self.assertEqual(bytes(emu.mem_read(src, len(packed))), packed)
            self.assertEqual(
                accesses, [len(packed), len(packed)] if blocks >= 2 else [0, 0]
            )
            self.assertEqual(emu.reg_read(regs.UC_ARM64_REG_SP), stack_top)
            for reg, value in preserved.items():
                self.assertEqual(emu.reg_read(reg) & ((1 << 64) - 1), value)
            for base in (src, dst):
                self.assertEqual(bytes(emu.mem_read(base - 64, 64)), guard)
                self.assertEqual(bytes(emu.mem_read(base + len(packed), 64)), guard)

    def test_results_bounds_repeat_calls_and_abi(self):
        for compiler, (code, symbols) in self.builds.items():
            for function, (entry, _) in symbols.items():
                for blocks in (0, 1, 2, 3, 4, 8, 32, 65):
                    for offset in (0, 4, 12):
                        with self.subTest(
                            compiler=compiler,
                            function=function,
                            blocks=blocks,
                            offset=offset,
                        ):
                            self.check_execution(code, entry, blocks, offset)

    def test_linux_harness_smoke(self):
        gcc = shutil.which("aarch64-linux-gnu-gcc")
        qemu = shutil.which("qemu-aarch64") or shutil.which("qemu-aarch64-static")
        if not gcc or not qemu:
            self.skipTest(
                "Linux cross compiler and QEMU required for harness smoke test"
            )
        binary = Path(self.directory.name) / "benchmark"
        subprocess.run(
            [
                gcc,
                "-O3",
                "-std=gnu11",
                "-march=armv8-a",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-static",
                EXAMPLE / "vector_abs_store_kernels.c",
                EXAMPLE / "vector_abs_store_bench.c",
                "-o",
                binary,
            ],
            check=True,
            capture_output=True,
        )
        # QEMU establishes functionality only, not a hardware timing advantage.
        for args in (("2", "3", "3"), ("3", "3", "4", "32"), ("32", "3", "3")):
            with self.subTest(args=args):
                result = subprocess.run(
                    [qemu, binary, *args],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertIn("Paired median ST1/STR time ratio:", result.stdout)
                if len(args) == 4:
                    self.assertIn("estimated cycles", result.stdout)
        for args in (
            ("1",),
            ("-1",),
            ("18446744073709551616",),
            ("2", " -1"),
            ("2", "0"),
            ("2", "1", "0"),
            ("2", "1", "1", "nan"),
            ("2", "1", "1", "-1"),
        ):
            with self.subTest(invalid_args=args):
                result = subprocess.run(
                    [qemu, binary, *args], capture_output=True, timeout=30
                )
                self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
