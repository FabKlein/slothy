"""Assembler checks and an independent semantic model, not a hardware emulator."""

from pathlib import Path
import random
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
NAIVE = ROOT / "examples/naive/armv8m/s8_dot_2x4/s8_dot_2x4_cm55.s"
OPT = ROOT / "examples/opt/armv8m/s8_dot_2x4/s8_dot_2x4_cm55_swpipe_u2.s"
ACCUMULATORS = (0, 2, 4, 6, 8, 10, 12, 14)
MASK = (1 << 32) - 1


def run_model(source, initial, buffers):
    """Interpret only the instructions used here, with exact load bounds."""
    labels, code = {}, []
    for raw in source.splitlines():
        text = raw.split("//", 1)[0].strip().lower()
        if not text or text.startswith("."):
            continue
        if text.endswith(":"):
            labels[text[:-1]] = len(code)
        else:
            code.append(text)
    regs, vectors = initial.copy(), {}
    pc, steps, carry = 0, 0, False
    while pc < len(code):
        steps += 1
        if steps > 10000:
            raise AssertionError("Loop did not terminate")
        line = code[pc]
        pc += 1
        load = re.fullmatch(r"vldrb\.8 q(\d), \[r(\d+)\], #16", line)
        dot = re.fullmatch(r"vmladava\.s8 r(\d+), q(\d), q(\d)", line)
        sub = re.fullmatch(r"subs? r7, r7, #(\d+)", line)
        cmp = re.fullmatch(r"cmp r7, #(\d+)", line)
        branch = re.fullmatch(r"(bhs|blo) (\w+)", line)
        if load:
            q, r = map(int, load.groups())
            addr = regs[r]
            if not 0 <= addr <= len(buffers[r]) - 16:
                raise AssertionError(f"Out-of-bounds load: {line} at {addr}")
            vectors[q] = buffers[r][addr:addr + 16]
            regs[r] += 16
        elif dot:
            r, qn, qm = map(int, dot.groups())
            regs[r] = (regs[r] + sum(a * b for a, b in zip(vectors[qn], vectors[qm]))) & MASK
        elif sub:
            regs[7] = (regs[7] - int(sub[1])) & MASK
        elif cmp:
            carry = regs[7] >= int(cmp[1])
        elif branch:
            if carry == (branch[1] == "bhs"):
                pc = labels[branch[2]]
        else:
            raise AssertionError(f"Unsupported instruction in semantic model: {line}")
    return regs


class S8DotLoopTests(unittest.TestCase):
    def test_numerical_results_and_byte_count_boundaries(self):
        naive, optimized = NAIVE.read_text(), OPT.read_text()
        counts = list(range(161)) + [191, 192, 193, 255, 256, 257, 511, 512, 513]
        for seed in (0, 55, 520):
            rng = random.Random(seed)
            for count in counts:
                with self.subTest(seed=seed, count=count):
                    blocks = count // 16
                    initial = {r: rng.getrandbits(32) for r in range(15)}
                    initial.update({1: 0, 3: 0, 5: 0, 7: count})
                    buffers = {
                        r: [rng.randrange(-128, 128) for _ in range(size * blocks)]
                        for r, size in ((1, 16), (3, 16), (5, 64))
                    }
                    expected = initial.copy()
                    for block in range(blocks):
                        for column in range(4):
                            weights = buffers[5][block * 64 + column * 16:][:16]
                            for row, ptr in enumerate((1, 3)):
                                acc = ACCUMULATORS[2 * column + row]
                                values = buffers[ptr][block * 16:][:16]
                                expected[acc] = (
                                    expected[acc] + sum(a * b for a, b in zip(values, weights))
                                ) & MASK
                    expected.update({1: blocks * 16, 3: blocks * 16, 5: blocks * 64, 7: count % 16})
                    self.assertEqual(run_model(optimized, initial, buffers), expected)
                    if count >= 16:  # The original do/while loop requires one full block.
                        self.assertEqual(run_model(naive, initial, buffers), expected)

    @unittest.skipUnless(shutil.which("clang-19"), "Clang 19 required")
    def test_assembly(self):
        with tempfile.TemporaryDirectory() as tmp:
            for source in (NAIVE, OPT):
                subprocess.run(
                    ["clang-19", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                     "-mfloat-abi=hard", "-mthumb", "-c", str(source),
                     "-o", str(Path(tmp) / "loop.o")], check=True,
                )


if __name__ == "__main__":
    unittest.main()
