# SPDX-License-Identifier: MIT
"""Operand-scoped timing refinements shared by the experimental Armv9 targets.

Only the checked forms are selected here; other forms retain their existing
model entries. See README.armv9-models.md for scope and remaining uncertainties.
"""

from slothy.targets.aarch64.aarch64_neon import (
    AArch64NeonLogical,
    add_imm,
    add_w_imm,
    adds,
    fmov_0,
    fmov_0_force_output,
    fmov_d_form,
    fmov_s_form,
    fmov_w_to_s,
    mov_wtov_s,
    mul_xform,
    vaddf,
    vand,
    vdup_w,
    veor,
    vmla,
    vmls,
    vmulf,
    vtbl_2,
)

FMOV_GPR_TO_VEC = (fmov_0, fmov_0_force_output, fmov_w_to_s)


def fmov_dependency_latency(src, out_idx, dst, *, add_to_fmov):
    """Override only the checked GPR-result paths into a same-width FMOV.

    ADDS also writes flags: the result index and register match are important.
    Keep untested widths, high-lane moves and other arithmetic forms unchanged.
    """
    if type(dst) in (fmov_0, fmov_0_force_output):
        transfer, add_forms, multiply = fmov_d_form, (add_imm, adds), mul_xform
    elif type(dst) is fmov_w_to_s:
        transfer, add_forms, multiply = fmov_s_form, (add_w_imm,), None
    else:
        return None
    if not (0 <= out_idx < len(src.args_out)):
        return None
    if src.args_out[out_idx] != dst.args_in[0]:
        return None
    if type(src) is transfer:
        return 4
    if type(src) in add_forms:
        return add_to_fmov
    if type(src) is multiply:
        return 5
    return None


def _arrangement(inst, arrangement):
    datatypes = inst.datatype
    if isinstance(datatypes, str):
        datatypes = [datatypes]
    return bool(datatypes) and all(dt.lower() == arrangement for dt in datatypes)


def is_fp32_vector_arithmetic(inst):
    return type(inst) in (vaddf, vmulf) and _arrangement(inst, "4s")


def is_and_eor_16b(inst):
    return type(inst) in (vand, veor) and _arrangement(inst, "16b")


def is_other_neon_logical(inst):
    return isinstance(inst, AArch64NeonLogical) and not is_and_eor_16b(inst)


def is_dual_issue_gpr_insert(inst):
    return (type(inst) is vdup_w and _arrangement(inst, "4s")) or (
        type(inst) is mov_wtov_s and inst.index == 0
    )


def forwarding_latency(src, dst):
    """Return a checked same-opcode bypass latency, or None for the default.

    These producers have exactly one result. If it also feeds an earlier-read
    consumer operand, the normal latency must win. Exact types intentionally
    exclude FP subclasses, lane forms and untested mixed MLA/MLS chains.
    """
    if type(src) is not type(dst):
        return None
    if (
        type(src) in (vmla, vmls)
        and _arrangement(src, "4s")
        and _arrangement(dst, "4s")
        and src.args_in_out[0] == dst.args_in_out[0]
        and src.args_in_out[0] not in dst.args_in
    ):
        return 2
    if (
        type(src) is vtbl_2
        and any(
            _arrangement(src, width) and _arrangement(dst, width)
            for width in ("8b", "16b")
        )
        and src.args_out[0] == dst.args_in[1]
        and src.args_out[0] not in (dst.args_in[0], dst.args_in[2])
    ):
        return 4
    return None
