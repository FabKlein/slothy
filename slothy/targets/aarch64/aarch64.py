#
# Copyright (c) 2022 Arm Limited
# Copyright (c) 2022 Hanno Becker
# Copyright (c) 2023 Amin Abdulrahman, Matthias Kannwischer
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

"""
Scalar-only AArch64 instruction helpers shared across targets.

Instruction metadata is described in JSON (see
``aarch64_scalar_instructions.json``) to avoid manually repeating boilerplate
for each variant. This module loads the specification, generates the
corresponding instruction subclasses, and registers them with the generic
parser exposed by :mod:`aarch64_neon`.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from slothy.targets.aarch64.instruction_loader import (
    generate_instruction_classes,
    read_instruction_specs,
)

from slothy.targets.aarch64.aarch64_neon import (
    AArch64Instruction,
    Instruction,
    Ldr_D,
    Ldr_Q,
    Ldr_X,
    Ldp_X,
)

# These base classes are referenced indirectly via the JSON specification.
_SCALAR_BASE_CLASSES = (Ldr_D, Ldr_Q, Ldr_X, Ldp_X)
del _SCALAR_BASE_CLASSES


class Ldr_S(AArch64Instruction):
    """Base class for scalar single-precision loads."""


class Str_S(AArch64Instruction):
    """Base class for scalar single-precision stores."""


class Ldp_S(AArch64Instruction):
    """Base class for scalar pair loads."""


class Stp_S(AArch64Instruction):
    """Base class for scalar pair stores."""


class Sfma(AArch64Instruction):
    """Base class for scalar fused multiply(-accumulate) instructions."""


class Smul(AArch64Instruction):
    """Base class for scalar FP multiply instructions."""


class AArch64BasicArithmetic(AArch64Instruction):
    """Base class for scalar add/sub style instructions."""


class AArch64ShiftedArithmetic(AArch64Instruction):
    """Base class for arithmetic ops with shifted operands."""


class AArch64Shift(AArch64Instruction):
    """Base class for scalar shift instructions."""


class AArch64Logical(AArch64Instruction):
    """Base class for scalar logical instructions."""


class AArch64LogicalShifted(AArch64Instruction):
    """Base class for scalar logical instructions with shifts."""


class AArch64ConditionalCompare(AArch64Instruction):
    """Base class for conditional compare instructions."""


class AArch64ConditionalSelect(AArch64Instruction):
    """Base class for conditional select instructions."""


class AArch64Move(AArch64Instruction):
    """Base class for scalar move/constant instructions."""


class AArch64HighMultiply(AArch64Instruction):
    """Base class for high multiply instructions."""


class AArch64Multiply(AArch64Instruction):
    """Base class for scalar multiply instructions."""


class AArch64CRC32(AArch64Instruction):
    """Base class for scalar CRC32 instructions."""


class Tst(AArch64Instruction):
    """Base class for test/compare instructions."""


def _register_instruction(inst_class):
    """Ensure Instruction parser knows about dynamically added classes."""
    leaves = Instruction.all_subclass_leaves

    # Newly added subclasses mean their ancestors are no longer leaves.
    for base in inst_class.__mro__[1:]:
        if base is Instruction:
            break
        if base in leaves:
            leaves.remove(base)

    if inst_class not in leaves:
        leaves.append(inst_class)


SPEC_PATH = Path(__file__).with_name("aarch64_scalar_instructions.json")
INSTRUCTION_SPECS = read_instruction_specs(SPEC_PATH)


BASE_EXPORTS: List[str] = [
    "Ldr_S",
    "Str_S",
    "Ldp_S",
    "Stp_S",
    "Sfma",
    "Smul",
    "AArch64BasicArithmetic",
    "AArch64ShiftedArithmetic",
    "AArch64Shift",
    "AArch64Logical",
    "AArch64LogicalShifted",
    "AArch64ConditionalCompare",
    "AArch64ConditionalSelect",
    "AArch64Move",
    "AArch64HighMultiply",
    "AArch64Multiply",
    "AArch64CRC32",
    "Tst",
]

GENERATED_EXPORTS = generate_instruction_classes(
    INSTRUCTION_SPECS, globals(), AArch64Instruction, _register_instruction
)


# Preserve the old public names while using upstream's canonical class names.
lsr_variable = globals()["lsr"]
csel_ne = globals()["csel"]

__all__ = BASE_EXPORTS + GENERATED_EXPORTS + ["lsr_variable", "csel_ne"]
