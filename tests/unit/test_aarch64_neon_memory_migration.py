"""Preserve memory semantics when moving boilerplate definitions into JSON."""

import json
import logging
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
from types import SimpleNamespace
import unittest

from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM
from unicorn.arm64_const import (
    UC_ARM64_REG_CPACR_EL1,
    UC_ARM64_REG_Q0,
    UC_ARM64_REG_X0,
    UC_ARM64_REG_X1,
    UC_ARM64_REG_X2,
)

from aarch64_model_snapshot import observe
from test_aarch64_neon_declarative_migration import TARGET_NAMES
from slothy.core.core import Result, SlothyBase
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as arch, cortex_a520
from slothy.targets.aarch64.isa import instruction_features
from slothy.targets.query import Archery

LOGGER = logging.getLogger(__name__)
HAS_ASSEMBLER = shutil.which("clang-19") and shutil.which("llvm-objcopy-19")


def fixture():
    path = Path(__file__).with_name("data") / "aarch64_neon_memory_before_json.json"
    return json.loads(path.read_text(encoding="utf8"))["cases"]


def parse(source):
    return arch.Instruction.parser(SourceLine(source))[0]


def assemble(source):
    with tempfile.TemporaryDirectory() as temp:
        obj = Path(temp) / "memory.o"
        binary = Path(temp) / "memory.bin"
        result = subprocess.run(
            [
                "clang-19",
                "--target=aarch64-none-elf",
                "-x",
                "assembler",
                "-c",
                "-",
                "-o",
                str(obj),
            ],
            input=".text\n" + source + "\n",
            text=True,
            capture_output=True,
        )
        if result.returncode:
            raise AssertionError(result.stderr)
        subprocess.run(
            [
                "llvm-objcopy-19",
                "-O",
                "binary",
                "--only-section=.text",
                str(obj),
                str(binary),
            ],
            capture_output=True,
            check=True,
        )
        return binary.read_bytes()


def machine(code):
    uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    uc.mem_map(0x10000, 0x1000)
    uc.mem_write(0x10000, code)
    uc.mem_map(0x20000, 0x3000)
    uc.reg_write(UC_ARM64_REG_CPACR_EL1, 3 << 20)
    return uc


class MemoryMigrationTests(unittest.TestCase):
    def test_parser_and_all_target_models_match_baseline(self):
        cases = fixture()
        self.assertEqual(len(cases), 26)
        definitions = {entry["name"] for entry in arch._NEON_SPECS}
        targets = [Archery.get_target(name) for name in TARGET_NAMES]
        for case in cases:
            with self.subTest(instruction=case["definition"]):
                self.assertIn(case["definition"], definitions)
                inst = parse(case["source"])
                actual = observe(case["source"], targets=targets)
                actual["offset_adjustable"] = inst.offset_adjustable
                actual["is_load_store"] = inst.is_load_store_instruction()
                self.assertEqual(json.loads(json.dumps(actual)), case["expected"])
                self.assertEqual(type(inst).__module__, arch.__name__)
                self.assertIn(type(inst), arch.Instruction.all_subclass_leaves)

    def test_explicit_isa_requirements(self):
        for case in fixture():
            inst = parse(case["source"])
            if case["definition"] == "prefetch":
                expected = set()
            elif case["source"].startswith(("ld1", "st1")):
                expected = {"FEAT_FP", "FEAT_AdvSIMD"}
            else:
                expected = {"FEAT_FP"}
            self.assertEqual(instruction_features(inst), expected, case["definition"])

    def test_adjusted_offsets_and_renamed_addresses_are_written(self):
        specs = {entry["name"]: entry for entry in arch._NEON_SPECS}
        for case in fixture():
            spec = specs[case["definition"]]
            if not spec.get("restore_immediate_from_pre_index"):
                continue
            with self.subTest(instruction=case["definition"]):
                inst = parse(case["source"])
                inst.pre_index = "32 + 16"
                addr = spec["addr_source"]
                if addr["type"] == "inputs":
                    inst.args_in[addr["index"]] = "x9"
                rewritten = parse(inst.write())
                self.assertEqual(int(rewritten.pre_index), 48)
                self.assertEqual(
                    rewritten.addr, "sp" if addr["type"] == "literal" else "x9"
                )

    def test_reordered_memory_offsets_are_fixed_in_both_directions(self):
        for op in ("ldr q1", "str q1", "ldp q1, q2", "stp q1, q2"):
            for increment_first in (False, True):
                with self.subTest(op=op, increment_first=increment_first):
                    inc = SimpleNamespace(inst=parse("ldr q0, [x0], #16"), fixup=0)
                    offset = SimpleNamespace(inst=parse(f"{op}, [x0, #32]"), fixup=0)
                    nodes = [inc, offset] if increment_first else [offset, inc]
                    Result._fixup_reordered_pair(*nodes, LOGGER)
                    Result._fixup_finish(nodes, LOGGER)
                    self.assertEqual(
                        int(parse(offset.inst.write()).pre_index),
                        48 if increment_first else 16,
                    )
                    self.assertEqual(int(parse(inc.inst.write()).increment), 16)

    @unittest.skipUnless(HAS_ASSEMBLER, "Requires AArch64-capable LLVM tools")
    def test_architectural_forms_assemble(self):
        # Hint pseudo-instructions, the legacy LD1 offset form, and the existing
        # PRFM hint spelling are preserved, not claimed as architectural syntax.
        legacy = {
            "q_ldr_with_imm_hint",
            "q_str_with_imm_hint",
            "q_ld1_with_inc",
            "prefetch",
        }
        assemble(
            "\n".join(
                parse(case["source"]).write()
                for case in fixture()
                if case["definition"] not in legacy
            )
        )

    @unittest.skipUnless(HAS_ASSEMBLER, "Requires AArch64-capable LLVM tools")
    def test_pre_and_post_index_load_store_execution(self):
        data = bytes(range(64))
        vector = bytes(range(128, 144))
        for op in ("ldr", "str"):
            for pre in (False, True):
                with self.subTest(op=op, pre=pre):
                    address = "[x0, #16]!" if pre else "[x0], #16"
                    inst = parse(f"{op} q0, {address}")
                    self.assertEqual(inst.args_in_out, ["x0"])
                    code = assemble(inst.write())
                    uc = machine(code)
                    uc.reg_write(UC_ARM64_REG_X0, 0x20000)
                    uc.reg_write(UC_ARM64_REG_Q0, int.from_bytes(vector, "little"))
                    uc.mem_write(0x20000, data)
                    uc.emu_start(0x10000, 0x10000 + len(code))
                    self.assertEqual(uc.reg_read(UC_ARM64_REG_X0), 0x20010)
                    offset = 16 if pre else 0
                    if op == "ldr":
                        self.assertEqual(
                            uc.reg_read(UC_ARM64_REG_Q0),
                            int.from_bytes(data[offset : offset + 16], "little"),
                        )
                        self.assertEqual(bytes(uc.mem_read(0x20000, 64)), data)
                    else:
                        expected = data[:offset] + vector + data[offset + 16 :]
                        self.assertEqual(bytes(uc.mem_read(0x20000, 64)), expected)

    @unittest.skipUnless(HAS_ASSEMBLER, "Requires AArch64-capable LLVM tools")
    def test_optimized_and_pipelined_memory_loop_execution(self):
        source = SourceLine.read_multiline(
            "ldp q0, q1, [x0], #32\n"
            "ld1r {v2.4s}, [x2], #4\n"
            "add v0.4s, v0.4s, v2.4s\n"
            "add v1.4s, v1.4s, v2.4s\n"
            "stp q0, q1, [x1], #32\n"
        )
        for pipelining in (False, True):
            with self.subTest(pipelining=pipelining):
                core = SlothyBase(arch, cortex_a520)
                core.config.outputs = {"x0", "x1", "x2"}
                core.config.selftest = False
                core.config.isa_check = "strict"
                core.config.sw_pipelining.enabled = pipelining
                if pipelining:
                    core.config.sw_pipelining.min_overlapping = 1
                core.config.variable_size = True
                core.config.constraints.stalls_allowed = 32
                core.config.timeout = 10
                self.assertTrue(core.optimize(source))
                if pipelining:
                    self.assertGreater(core.result.num_exceptional_iterations, 0)
                    original, optimized = core.result.get_fully_unrolled_loop(4)
                else:
                    original, optimized = source * 4, core.result.code * 4
                for lines in (original, optimized):
                    code = assemble("\n".join(line.text for line in lines))
                    uc = machine(code)
                    uc.reg_write(UC_ARM64_REG_X0, 0x20000)
                    uc.reg_write(UC_ARM64_REG_X1, 0x21000)
                    uc.reg_write(UC_ARM64_REG_X2, 0x22000)
                    uc.mem_write(0x20000, struct.pack("<32I", *range(32)))
                    uc.mem_write(0x22000, struct.pack("<4I", *range(50, 54)))
                    uc.emu_start(0x10000, 0x10000 + len(code))
                    self.assertEqual(uc.reg_read(UC_ARM64_REG_X0), 0x20080)
                    self.assertEqual(uc.reg_read(UC_ARM64_REG_X1), 0x21080)
                    self.assertEqual(uc.reg_read(UC_ARM64_REG_X2), 0x22010)
                    expected = struct.pack(
                        "<32I", *(i + 50 + i // 8 for i in range(32))
                    )
                    self.assertEqual(bytes(uc.mem_read(0x21000, 128)), expected)
                    self.assertEqual(bytes(uc.mem_read(0x21080, 16)), bytes(16))


if __name__ == "__main__":
    unittest.main()
