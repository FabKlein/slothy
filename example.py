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
# Author: Hanno Becker <hannobecker@posteo.de>
#

import argparse, logging
from io import StringIO

from slothy.slothy import Slothy
from slothy.core import Config

import targets.arm_v81m.arch_v81m as Arch_Armv81M
import targets.arm_v81m.cortex_m55r1 as Target_CortexM55r1
import targets.arm_v81m.cortex_m85r1 as Target_CortexM85r1

import targets.aarch64.aarch64_neon as AArch64_Neon
import targets.aarch64.cortex_a55 as Target_CortexA55
import targets.aarch64.cortex_a72_frontend as Target_CortexA72

target_label_dict = {Target_CortexA55: "a55",
                     Target_CortexA72: "a72",
                     Target_CortexM55r1: "m55",
                     Target_CortexM85r1: "m85"}


class Example():
    def __init__(self, infile, name=None, funcname=None, suffix="opt", 
                 rename=False, outfile="", arch=Arch_Armv81M, target=Target_CortexM55r1,
                 **kwargs):
        if name == None:
            name = infile

        self.arch = arch
        self.target = target
        self.funcname = funcname
        self.infile = infile
        self.suffix = suffix
        if outfile == "":
            self.outfile = f"{infile}_{self.suffix}_{target_label_dict[self.target]}"
        else:
            self.outfile = f"{outfile}_{self.suffix}_{target_label_dict[self.target]}"
        if funcname == None:
            self.funcname = self.infile
        subfolder = ""
        if self.arch == AArch64_Neon:
            subfolder = "aarch64/"
        self.infile_full  = f"examples/naive/{subfolder}{self.infile}.s"
        self.outfile_full = f"examples/opt/{subfolder}{self.outfile}.s"
        self.name = name
        self.rename = rename

        self.extra_args = kwargs
    # By default, optimize the whole file
    def core(self, helight):
        helight.optimize()
    def run(self, debug=False):
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.INFO)
        logger = logging.getLogger(self.name).getChild("helight55")
        logger.addHandler(handler)
        helight = Slothy(self.arch, self.target,
                         debug=debug, logger=logger)
        helight.load_source_from_file(self.infile_full)
        self.core(helight, *self.extra_args)

        if self.rename:
            helight.rename_function(self.funcname, f"{self.funcname}_{self.suffix}_{target_label_dict[self.target]}")
        helight.write_source_to_file(self.outfile_full)

        return self.outfile_full, log_stream.getvalue()


class Example0(Example):
    def __init__(self):
        super().__init__("simple0")

class Example1(Example):
    def __init__(self):
        super().__init__("simple1")

class Example2(Example):
    def __init__(self):
        super().__init__("simple0_loop")
    def core(self,helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.typing_hints["const"] = Arch_Armv81M.RegisterType.GPR
        helight.optimize_loop("start")

class Example3(Example):
    def __init__(self):
        super().__init__("simple1_loop")
    def core(self,helight):
        helight.config.sw_pipelining.enabled = True
        helight.optimize_loop("start")

class SBCSample(Example):
    def __init__(self):
        super().__init__("sbc")
    def core(self,helight):
        helight.config.split_heuristic = True
        helight.config.allow_useless_instructions = True
        helight.config.split_heuristic_factor = 2
        helight.config.typing_hints = { 'cst' :
                Arch_Armv81M.RegisterType.GPR,
                                        'out' :
                Arch_Armv81M.RegisterType.GPR }
        helight.optimize()

class CRT(Example):
    def __init__(self):
        super().__init__("crt")
    def core(self,helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.selfcheck = True
        # Double the loop body to create more interleaving opportunities
        # Basically a tradeoff of code-size vs performance
        helight.config.sw_pipelining.unroll = 2
        helight.config.typing_hints = {
            "const_prshift"  : Arch_Armv81M.RegisterType.GPR,
            "const_shift9"   : Arch_Armv81M.RegisterType.GPR,
            "p_inv_mod_q"    : Arch_Armv81M.RegisterType.GPR,
            "p_inv_mod_q_tw" : Arch_Armv81M.RegisterType.GPR,
            "mod_p"          : Arch_Armv81M.RegisterType.GPR,
            "mod_p_tw"       : Arch_Armv81M.RegisterType.GPR,
        }
        helight.optimize()

class ntt_n256_l6_s32(Example):
    def __init__(self,var):
        super().__init__(f"ntt_n256_l6_s32_{var}")
    def core(self,helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.typing_hints = { r : Arch_Armv81M.RegisterType.GPR for r in
           [ "root0",         "root1",         "root2",
             "root0_twisted", "root1_twisted", "root2_twisted" ] }
        helight.optimize_loop("layer12_loop")
        helight.optimize_loop("layer34_loop")
        helight.optimize_loop("layer56_loop")

class ntt_n256_l8_s32(Example):
    def __init__(self,var):
        super().__init__(f"ntt_n256_l8_s32_{var}")
    def core(self,helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.typing_hints = {
            "root0"         : Arch_Armv81M.RegisterType.GPR,
            "root1"         : Arch_Armv81M.RegisterType.GPR,
            "root2"         : Arch_Armv81M.RegisterType.GPR,
            "root0_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root1_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root2_twisted" : Arch_Armv81M.RegisterType.GPR,
        }
        helight.optimize_loop("layer12_loop")
        helight.optimize_loop("layer34_loop")
        helight.optimize_loop("layer56_loop")
        helight.config.typing_hints = {}
        helight.optimize_loop("layer78_loop")

class intt_n256_l6_s32(Example):
    def __init__(self, var):
        super().__init__(f"intt_n256_l6_s32_{var}")
    def core(self,helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.typing_hints = {
            "root0"         : Arch_Armv81M.RegisterType.GPR,
            "root1"         : Arch_Armv81M.RegisterType.GPR,
            "root2"         : Arch_Armv81M.RegisterType.GPR,
            "root0_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root1_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root2_twisted" : Arch_Armv81M.RegisterType.GPR,
        }
        helight.optimize_loop("layer12_loop")
        helight.optimize_loop("layer34_loop")
        helight.optimize_loop("layer56_loop")

class intt_n256_l8_s32(Example):
    def __init__(self, var):
        super().__init__(f"intt_n256_l8_s32_{var}")
    def core(self,helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.typing_hints = {
            "root0"         : Arch_Armv81M.RegisterType.GPR,
            "root1"         : Arch_Armv81M.RegisterType.GPR,
            "root2"         : Arch_Armv81M.RegisterType.GPR,
            "root0_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root1_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root2_twisted" : Arch_Armv81M.RegisterType.GPR,
        }
        helight.optimize_loop("layer12_loop")
        helight.optimize_loop("layer34_loop")
        helight.optimize_loop("layer56_loop")
        helight.config.typing_hints = {}
        helight.optimize_loop("layer78_loop")


class ntt_kyber_1_23_45_67(Example):
    def __init__(self, var="", arch=Arch_Armv81M, target=Target_CortexM55r1):
        name = "ntt_kyber_1_23_45_67"
        infile = name
        if var != "":
            name += f"_{var}"
            infile += f"_{var}"
        name += f"_{target_label_dict[target]}"
        super().__init__(infile, name=name, arch=arch, target=target, rename=True)
        self.var = var
    def core(self, helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.typing_hints = {
            "root0"         : Arch_Armv81M.RegisterType.GPR,
            "root1"         : Arch_Armv81M.RegisterType.GPR,
            "root2"         : Arch_Armv81M.RegisterType.GPR,
            "root0_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root1_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root2_twisted" : Arch_Armv81M.RegisterType.GPR,
        }
        helight.config.inputs_are_outputs = True
        helight.optimize_loop("layer1_loop")
        helight.optimize_loop("layer23_loop")
        helight.optimize_loop("layer45_loop")
        helight.config.constraints.st_ld_hazard = False
        if "no_trans" in self.var:
            helight.config.constraints.st_ld_hazard = True
        helight.config.typing_hints = {}
        helight.optimize_loop("layer67_loop")

class ntt_kyber_1(Example):
    def __init__(self, arch=Arch_Armv81M, target=Target_CortexM55r1):
        name = "ntt_kyber_1"
        infile = "ntt_kyber_1_23_45_67"

        name += f"_{target_label_dict[target]}"
        super().__init__(infile, name=name, arch=arch, target=target, rename=True)

    def core(self, helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.inputs_are_outputs = True
        helight.config.sw_pipelining.minimize_overlapping = False
        helight.config.sw_pipelining.optimize_preamble = False
        helight.config.sw_pipelining.optimize_postamble = False
        helight.config.typing_hints = {
            "root0"         : Arch_Armv81M.RegisterType.GPR,
            "root1"         : Arch_Armv81M.RegisterType.GPR,
            "root2"         : Arch_Armv81M.RegisterType.GPR,
            "root0_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root1_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root2_twisted" : Arch_Armv81M.RegisterType.GPR,
        }
        helight.optimize_loop("layer1_loop")

class ntt_kyber_23(Example):
    def __init__(self, arch=Arch_Armv81M, target=Target_CortexM55r1):
        name = "ntt_kyber_23"
        infile = "ntt_kyber_1_23_45_67"

        name += f"_{target_label_dict[target]}"
        super().__init__(infile, name=name, arch=arch, target=target, rename=True)

    def core(self, helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.inputs_are_outputs = True
        helight.config.sw_pipelining.minimize_overlapping = False
        helight.config.sw_pipelining.optimize_preamble = False
        helight.config.sw_pipelining.optimize_postamble = False
        helight.config.typing_hints = {
            "root0"         : Arch_Armv81M.RegisterType.GPR,
            "root1"         : Arch_Armv81M.RegisterType.GPR,
            "root2"         : Arch_Armv81M.RegisterType.GPR,
            "root0_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root1_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root2_twisted" : Arch_Armv81M.RegisterType.GPR,
        }
        helight.optimize_loop("layer23_loop")

class ntt_kyber_45(Example):
    def __init__(self, arch=Arch_Armv81M, target=Target_CortexM55r1):
        name = "ntt_kyber_45"
        infile = "ntt_kyber_1_23_45_67"

        name += f"_{target_label_dict[target]}"
        super().__init__(infile, name=name, arch=arch, target=target, rename=True)

    def core(self, helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.inputs_are_outputs = True
        helight.config.sw_pipelining.minimize_overlapping = False
        helight.config.sw_pipelining.optimize_preamble = False
        helight.config.sw_pipelining.optimize_postamble = False
        helight.config.typing_hints = {
            "root0"         : Arch_Armv81M.RegisterType.GPR,
            "root1"         : Arch_Armv81M.RegisterType.GPR,
            "root2"         : Arch_Armv81M.RegisterType.GPR,
            "root0_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root1_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root2_twisted" : Arch_Armv81M.RegisterType.GPR,
        }
        helight.optimize_loop("layer45_loop")

class ntt_kyber_67(Example):
    def __init__(self, arch=Arch_Armv81M, target=Target_CortexM55r1):
        name = "ntt_kyber_67"
        infile = "ntt_kyber_1_23_45_67"

        name += f"_{target_label_dict[target]}"
        super().__init__(infile, name=name, arch=arch, target=target, rename=True)

    def core(self, helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.inputs_are_outputs = True
        helight.config.sw_pipelining.minimize_overlapping = False
        helight.config.sw_pipelining.optimize_preamble = False
        helight.config.sw_pipelining.optimize_postamble = False
        helight.config.constraints.st_ld_hazard = False
        helight.config.typing_hints = {}
        helight.optimize_loop("layer67_loop")

class ntt_kyber_12_345_67(Example):
    def __init__(self, cross_loops_optim=False, var="", arch=Arch_Armv81M, target=Target_CortexM55r1):
        infile = "ntt_kyber_12_345_67"
        if cross_loops_optim:
            name = "ntt_kyber_12_345_67_speed"
            suffix = "opt_speed"
        else:
            name = "ntt_kyber_12_345_67_size"
            suffix = "opt_size"
        if var != "":
            name += f"_{var}"
            infile += f"_{var}"
        name += f"_{target_label_dict[target]}"
        self.var=var
        super().__init__(infile, name=name,
                         suffix=suffix, rename=True, arch=arch, target=target)
        self.cross_loops_optim = cross_loops_optim

    def core(self,helight):
        helight.config.inputs_are_outputs = True
        helight.config.sw_pipelining.enabled = True
        helight.optimize_loop("layer12_loop", end_of_loop_label="layer12_loop_end")
        helight.config.constraints.stalls_first_attempt = 16
        helight.config.locked_registers = set( [ f"QSTACK{i}" for i in [4,5,6] ] +
                                               [ "STACK0" ] )
        if not self.cross_loops_optim:
            if "no_trans" not in self.var and "trans" in self.var:
                helight.config.constraints.st_ld_hazard = False  # optional, if it takes too long
            helight.config.sw_pipelining.enabled = False
            helight.optimize_loop("layer345_loop")
        else:
            if "no_trans" not in self.var and "trans" in self.var:
                helight.config.constraints.st_ld_hazard = False  # optional, if it takes too long
            helight.config.sw_pipelining.enabled = True
            helight.config.sw_pipelining.halving_heuristic = True
            helight.config.sw_pipelining.halving_heuristic_periodic = True
            helight.optimize_loop("layer345_loop", end_of_loop_label="layer345_loop_end")
            layer345_deps = helight.last_result.kernel_input_output.copy()

        helight.config.sw_pipelining.enabled = True
        helight.config.sw_pipelining.halving_heuristic = False
        helight.config.sw_pipelining.halving_heuristic_periodic = True
        helight.config.constraints.st_ld_hazard = False
        helight.optimize_loop("layer67_loop")
        layer67_deps = helight.last_result.kernel_input_output.copy()

        if self.cross_loops_optim:
            helight.config.inputs_are_outputs = False
            helight.config.constraints.st_ld_hazard = True
            helight.config.sw_pipelining.enabled = False
            helight.config.outputs = layer345_deps + ["r14"]
            helight.optimize(start="layer12_loop_end", end="layer345_loop")
            helight.config.outputs = layer67_deps + ["r14"]
            helight.optimize(start="layer345_loop_end", end="layer67_loop")


class ntt_kyber_12(Example):
    def __init__(self, arch=Arch_Armv81M, target=Target_CortexM55r1):
        name = "ntt_kyber_12"
        infile = "ntt_kyber_12_345_67"
        name += f"_{target_label_dict[target]}"
        super().__init__(infile, name=name, rename=True, arch=arch, target=target)

    def core(self, helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.inputs_are_outputs = True
        helight.config.sw_pipelining.minimize_overlapping = False
        helight.config.sw_pipelining.optimize_preamble = False
        helight.config.sw_pipelining.optimize_postamble = False
        helight.optimize_loop("layer12_loop", end_of_loop_label="layer12_loop_end")


class ntt_kyber_345(Example):
    def __init__(self, arch=Arch_Armv81M, target=Target_CortexM55r1):
        name = "ntt_kyber_345"
        infile = "ntt_kyber_12_345_67"
        name += f"_{target_label_dict[target]}"
        super().__init__(infile, name=name, rename=True, arch=arch, target=target)

    def core(self, helight):
        helight.config.locked_registers = set([f"QSTACK{i}" for i in [4, 5, 6]] +
                                              ["STACK0"])
        helight.config.sw_pipelining.enabled = True
        helight.config.inputs_are_outputs = True
        helight.config.sw_pipelining.minimize_overlapping = False
        helight.config.sw_pipelining.optimize_preamble = False
        helight.config.sw_pipelining.optimize_postamble = False
        helight.optimize_loop("layer345_loop")


class ntt_kyber_l345_symbolic(Example):
    def __init__(self):
        super().__init__("ntt_kyber_layer345_symbolic")
    def core(self,helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.sw_pipelining.halving_heuristic = True
        helight.config.sw_pipelining.halving_heuristic_periodic = True
        helight.optimize_loop("layer345_loop")


class ntt_kyber_123_4567(Example):
    def __init__(self, var="", arch=AArch64_Neon, target=Target_CortexA55):
        name = "ntt_kyber_123_4567"
        infile = name

        if var != "":
            name += f"_{var}"
            infile += f"_{var}"
        name += f"_{target_label_dict[target]}"

        super().__init__(infile, name, rename=True, arch=arch, target=target)

    def core(self, nelight):
        nelight.config.sw_pipelining.enabled = True
        nelight.config.inputs_are_outputs = True
        nelight.config.sw_pipelining.minimize_overlapping = False
        nelight.config.variable_size = True
        nelight.config.reserved_regs = [f"x{i}" for i in range(0, 7)] + ["x30", "sp"]
        nelight.config.constraints.stalls_first_attempt = 64
        nelight.optimize_loop("layer123_start")
        nelight.optimize_loop("layer4567_start")


class ntt_kyber_123(Example):
    def __init__(self, var="", arch=AArch64_Neon, target=Target_CortexA55):
        name = "ntt_kyber_123"
        infile = "ntt_kyber_123_4567"

        if var != "":
            name += f"_{var}"
            infile += f"_{var}"
        name += f"_{target_label_dict[target]}"

        super().__init__(infile, name, outfile=name, rename=True, arch=arch, target=target)

    def core(self, nelight):
        nelight.config.sw_pipelining.enabled = True
        nelight.config.inputs_are_outputs = True
        nelight.config.sw_pipelining.minimize_overlapping = False
        nelight.config.sw_pipelining.optimize_preamble = False
        nelight.config.sw_pipelining.optimize_postamble = False
        nelight.config.reserved_regs = [f"x{i}" for i in range(0, 7)] + ["x30", "sp"]
        nelight.optimize_loop("layer123_start")


class ntt_kyber_4567(Example):
    def __init__(self, var="", arch=AArch64_Neon, target=Target_CortexA55):
        name = "ntt_kyber_4567"
        infile = "ntt_kyber_123_4567"

        if var != "":
            name += f"_{var}"
            infile += f"_{var}"
        name += f"_{target_label_dict[target]}"

        super().__init__(infile, name, outfile=name, rename=True, arch=arch, target=target)

    def core(self, nelight):
        nelight.config.sw_pipelining.enabled = True
        nelight.config.inputs_are_outputs = True
        nelight.config.sw_pipelining.minimize_overlapping = False
        nelight.config.sw_pipelining.optimize_preamble = False
        nelight.config.sw_pipelining.optimize_postamble = False
        nelight.config.reserved_regs = [f"x{i}" for i in range(0, 7)] + ["x30", "sp"]
        nelight.optimize_loop("layer4567_start")


class ntt_kyber_1234_567(Example):
    def __init__(self, var="", arch=AArch64_Neon, target=Target_CortexA72):
        name = "ntt_kyber_1234_567"
        infile = name

        if var != "":
            name += f"_{var}"
            infile += f"_{var}"
        name += f"_{target_label_dict[target]}"

        super().__init__(infile, name, rename=True, arch=arch, target=target)
    def core(self,nelight):
        nelight.config.sw_pipelining.enabled = True
        nelight.config.inputs_are_outputs = True
        nelight.config.sw_pipelining.minimize_overlapping=False
        nelight.config.sw_pipelining.halving_heuristic = True
        nelight.config.variable_size = True
        nelight.config.reserved_regs = [f"x{i}" for i in range(0,6)] + ["x30", "sp"]
        nelight.config.split_heuristic = True
        nelight.config.split_heuristic_factor = 2
        nelight.config.split_heuristic_stepsize = 0.1
        nelight.config.split_heuristic_repeat = 4
        nelight.config.constraints.stalls_first_attempt = 40
        nelight.config.max_solutions = 64

        nelight.optimize_loop("layer1234_start")

        # layer567 is small enough for SW pipelining without heuristics
        nelight.config = Config(self.arch, self.target)
        nelight.config.sw_pipelining.enabled = True
        nelight.config.inputs_are_outputs = True
        nelight.config.sw_pipelining.minimize_overlapping = False
        nelight.config.variable_size = True
        nelight.config.reserved_regs = [f"x{i}" for i in range(0, 6)] + ["x30", "sp"]
        nelight.config.constraints.stalls_first_attempt = 64

        nelight.optimize_loop("layer567_start")

class ntt_kyber_1234(Example):
    def __init__(self, var="", arch=AArch64_Neon, target=Target_CortexA72):
        name = "ntt_kyber_1234"
        infile = "ntt_kyber_1234_567"

        if var != "":
            name += f"_{var}"
            infile += f"_{var}"
        name += f"_{target_label_dict[target]}"

        super().__init__(infile, name, outfile=name, rename=True, arch=arch, target=target)

    def core(self, nelight):
        nelight.config.sw_pipelining.enabled = True
        nelight.config.inputs_are_outputs = True
        nelight.config.sw_pipelining.minimize_overlapping = False
        nelight.config.sw_pipelining.optimize_preamble = False
        nelight.config.sw_pipelining.optimize_postamble = False
        nelight.config.reserved_regs = [f"x{i}" for i in range(0, 6)] + ["x30", "sp"]

        nelight.optimize_loop("layer1234_start")


class ntt_kyber_567(Example):
    def __init__(self, var="", arch=AArch64_Neon, target=Target_CortexA72):
        name = "ntt_kyber_567"
        infile = "ntt_kyber_1234_567"

        if var != "":
            name += f"_{var}"
            infile += f"_{var}"
        name += f"_{target_label_dict[target]}"

        super().__init__(infile, name, outfile=name, rename=True, arch=arch, target=target)

    def core(self, nelight):
        # layer567 is small enough for SW pipelining without heuristics
        nelight.config = Config(self.arch, self.target)
        nelight.config.sw_pipelining.enabled = True
        nelight.config.inputs_are_outputs = True
        nelight.config.sw_pipelining.minimize_overlapping = False
        nelight.config.sw_pipelining.optimize_preamble = False
        nelight.config.sw_pipelining.optimize_postamble = False
        nelight.config.reserved_regs = [f"x{i}" for i in range(0, 6)] + ["x30", "sp"]

        nelight.optimize_loop("layer567_start")


class intt_kyber_1_23_45_67(Example):
    def __init__(self):
        super().__init__("intt_kyber_1_23_45_67", rename=True)
    def core(self,helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.typing_hints = {
            "root0"         : Arch_Armv81M.RegisterType.GPR,
            "root1"         : Arch_Armv81M.RegisterType.GPR,
            "root2"         : Arch_Armv81M.RegisterType.GPR,
            "root0_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root1_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root2_twisted" : Arch_Armv81M.RegisterType.GPR,
        }
        helight.optimize_loop("layer1_loop")
        helight.optimize_loop("layer23_loop")
        helight.optimize_loop("layer45_loop")
        helight.config.typing_hints = {}
        helight.optimize_loop("layer67_loop")

class ntt_dilithium_12_34_56_78(Example):
    def __init__(self, var="", target=Target_CortexM55r1, arch=Arch_Armv81M):
        infile = "ntt_dilithium_12_34_56_78"
        name = infile
        if var != "":
            name += f"_{var}"
            infile += f"_{var}"
        name += f"_{target_label_dict[target]}"
        super().__init__(infile, name=name, arch=arch, target=target, rename=True)
        self.var = var
    def core(self, helight):
        helight.config.inputs_are_outputs = True
        helight.config.sw_pipelining.enabled = True
        helight.config.typing_hints = {
            "root0"         : Arch_Armv81M.RegisterType.GPR,
            "root1"         : Arch_Armv81M.RegisterType.GPR,
            "root2"         : Arch_Armv81M.RegisterType.GPR,
            "root0_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root1_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root2_twisted" : Arch_Armv81M.RegisterType.GPR,
            "const1"        : Arch_Armv81M.RegisterType.GPR,
        }
        helight.optimize_loop("layer12_loop")
        helight.optimize_loop("layer34_loop")
        helight.config.sw_pipelining.optimize_preamble  = True
        helight.config.sw_pipelining.optimize_postamble = False
        helight.optimize_loop("layer56_loop", end_of_loop_label="layer56_loop_end")
        helight.config.sw_pipelining.optimize_preamble  = False
        helight.config.sw_pipelining.optimize_postamble = True
        helight.config.typing_hints = {}
        helight.config.constraints.st_ld_hazard = False
        helight.optimize_loop("layer78_loop")
        # Optimize seams between loops
        # Make sure we preserve the inputs to the loop body
        helight.config.outputs = helight.last_result.kernel_input_output + ["r14"]
        helight.config.constraints.st_ld_hazard = True
        helight.config.sw_pipelining.enabled = False
        helight.optimize(start="layer56_loop_end", end="layer78_loop")

class ntt_dilithium_12(Example):
    def __init__(self, arch=Arch_Armv81M, target=Target_CortexM55r1):
        name = "ntt_dilithium_12"
        infile = "ntt_dilithium_12_34_56_78"
        name += f"_{target_label_dict[target]}"
        super().__init__(infile, name=name, arch=arch, target=target, rename=True)
    def core(self, helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.inputs_are_outputs = True
        helight.config.typing_hints = {
            "root0"         : Arch_Armv81M.RegisterType.GPR,
            "root1"         : Arch_Armv81M.RegisterType.GPR,
            "root2"         : Arch_Armv81M.RegisterType.GPR,
            "root0_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root1_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root2_twisted" : Arch_Armv81M.RegisterType.GPR,
            "const1"        : Arch_Armv81M.RegisterType.GPR,
        }
        helight.config.sw_pipelining.minimize_overlapping = False
        helight.config.sw_pipelining.optimize_preamble = False
        helight.config.sw_pipelining.optimize_postamble = False

        helight.optimize_loop("layer12_loop")

class ntt_dilithium_34(Example):
    def __init__(self, arch=Arch_Armv81M, target=Target_CortexM55r1):
        name = "ntt_dilithium_34"
        infile = "ntt_dilithium_12_34_56_78"
        name += f"_{target_label_dict[target]}"
        super().__init__(infile, name=name, arch=arch, target=target, rename=True)
    def core(self, helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.inputs_are_outputs = True
        helight.config.typing_hints = {
            "root0"         : Arch_Armv81M.RegisterType.GPR,
            "root1"         : Arch_Armv81M.RegisterType.GPR,
            "root2"         : Arch_Armv81M.RegisterType.GPR,
            "root0_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root1_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root2_twisted" : Arch_Armv81M.RegisterType.GPR,
            "const1"        : Arch_Armv81M.RegisterType.GPR,
        }
        helight.config.sw_pipelining.minimize_overlapping = False
        helight.config.sw_pipelining.optimize_preamble = False
        helight.config.sw_pipelining.optimize_postamble = False

        helight.optimize_loop("layer34_loop")

class ntt_dilithium_56(Example):
    def __init__(self, arch=Arch_Armv81M, target=Target_CortexM55r1):
        name = "ntt_dilithium_56"
        infile = "ntt_dilithium_12_34_56_78"
        name += f"_{target_label_dict[target]}"
        super().__init__(infile, name=name, arch=arch, target=target, rename=True)
    def core(self, helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.inputs_are_outputs = True
        helight.config.typing_hints = {
            "root0"         : Arch_Armv81M.RegisterType.GPR,
            "root1"         : Arch_Armv81M.RegisterType.GPR,
            "root2"         : Arch_Armv81M.RegisterType.GPR,
            "root0_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root1_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root2_twisted" : Arch_Armv81M.RegisterType.GPR,
            "const1"        : Arch_Armv81M.RegisterType.GPR,
        }
        helight.config.sw_pipelining.minimize_overlapping = False
        helight.config.sw_pipelining.optimize_preamble = False
        helight.config.sw_pipelining.optimize_postamble = False

        helight.optimize_loop("layer56_loop")

class ntt_dilithium_78(Example):
    def __init__(self, arch=Arch_Armv81M, target=Target_CortexM55r1):
        name = "ntt_dilithium_78"
        infile = "ntt_dilithium_12_34_56_78"
        name += f"_{target_label_dict[target]}"
        super().__init__(infile, name=name, arch=arch, target=target, rename=True)
    def core(self, helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.inputs_are_outputs = True
        helight.config.typing_hints = {}
        helight.config.sw_pipelining.minimize_overlapping = False
        helight.config.sw_pipelining.optimize_preamble = False
        helight.config.sw_pipelining.optimize_postamble = False

        helight.optimize_loop("layer78_loop")

class ntt_dilithium_123_456_78(Example):
    def __init__(self, cross_loops_optim=False, var="", arch=Arch_Armv81M, target=Target_CortexM55r1):
        infile = "ntt_dilithium_123_456_78"
        if cross_loops_optim:
            name = "ntt_dilithium_123_456_78_speed"
            suffix = "opt_speed"
        else:
            name = "ntt_dilithium_123_456_78_size"
            suffix = "opt_size"
        if var != "":
            name += f"_{var}"
            infile += f"_{var}"
        name += f"_{target_label_dict[target]}"
        super().__init__(infile, name=name,
                         suffix=suffix, arch=arch, target=target, rename=True)
        self.cross_loops_optim = cross_loops_optim
        self.var = var
    def core(self, helight):
        helight.config.inputs_are_outputs = True
        helight.config.typing_hints = {
            "root2"         : Arch_Armv81M.RegisterType.GPR,
            "root3"         : Arch_Armv81M.RegisterType.GPR,
            "root5"         : Arch_Armv81M.RegisterType.GPR,
            "root6"         : Arch_Armv81M.RegisterType.GPR,
            "rtmp"          : Arch_Armv81M.RegisterType.GPR,
            "rtmp_tw"       : Arch_Armv81M.RegisterType.GPR,
            "root2_tw"      : Arch_Armv81M.RegisterType.GPR,
            "root3_tw"      : Arch_Armv81M.RegisterType.GPR,
            "root5_tw"      : Arch_Armv81M.RegisterType.GPR,
            "root6_tw"      : Arch_Armv81M.RegisterType.GPR,
        }
        helight.config.constraints.stalls_minimum_attempt = 0
        helight.config.constraints.stalls_first_attempt = 0
        helight.config.locked_registers = set([f"QSTACK{i}" for i in [4, 5, 6]] +
                                              [f"ROOT{i}_STACK" for i in [0, 1, 4]] + ["RPTR_STACK"])
        if self.var != "" or ("speed" in self.name and self.target == Target_CortexM85r1):
            helight.config.constraints.st_ld_hazard = False  # optional, if it takes too long
        if not self.cross_loops_optim:
            helight.config.sw_pipelining.enabled=False
            helight.optimize_loop("layer123_loop")
            helight.optimize_loop("layer456_loop")
        else:
            helight.config.sw_pipelining.enabled = True
            helight.config.sw_pipelining.halving_heuristic = True
            helight.config.sw_pipelining.halving_heuristic_periodic = True
            helight.optimize_loop("layer123_loop", end_of_loop_label="layer123_loop_end")
            helight.optimize_loop("layer456_loop", end_of_loop_label="layer456_loop_end")

        helight.config.constraints.st_ld_hazard = False
        helight.config.sw_pipelining.enabled = True
        helight.config.sw_pipelining.halving_heuristic = False
        helight.config.typing_hints = {}
        helight.optimize_loop("layer78_loop")

        if self.cross_loops_optim:
            helight.config.sw_pipelining.enabled = False
            helight.config.constraints.st_ld_hazard = True
            helight.config.outputs = helight.last_result.kernel_input_output + ["r14"]
            helight.optimize(start="layer456_loop_end", end="layer78_loop")


class ntt_dilithium_123_456_78_symbolic(Example):
    def __init__(self):
        super().__init__("ntt_dilithium_123_456_78_symbolic", rename=True)
    def core(self,helight):
        helight.config.typing_hints = {
            "root2"         : Arch_Armv81M.RegisterType.GPR,
            "root3"         : Arch_Armv81M.RegisterType.GPR,
            "root5"         : Arch_Armv81M.RegisterType.GPR,
            "root6"         : Arch_Armv81M.RegisterType.GPR,
            "rtmp"          : Arch_Armv81M.RegisterType.GPR,
            "rtmp_tw"       : Arch_Armv81M.RegisterType.GPR,
            "root2_tw"      : Arch_Armv81M.RegisterType.GPR,
            "root3_tw"      : Arch_Armv81M.RegisterType.GPR,
            "root5_tw"      : Arch_Armv81M.RegisterType.GPR,
            "root6_tw"      : Arch_Armv81M.RegisterType.GPR,
        }
        helight.config.sw_pipelining.enabled=True
        helight.config.constraints.stalls_minimum_attempt = 0
        helight.config.constraints.stalls_first_attempt = 0
        helight.config.locked_registers = set( [ f"QSTACK{i}" for i in [4,5,6] ] +
                                               [ "ROOT0_STACK", "RPTR_STACK" ] )
        helight.optimize_loop("layer456_loop")

class ntt_dilithium_123_45678(Example):
    def __init__(self, var="", arch=AArch64_Neon, target=Target_CortexA55):
        name = f"ntt_dilithium_123_45678"
        infile = name

        if var != "":
            name += f"_{var}"
            infile += f"_{var}"
        name += f"_{target_label_dict[target]}"

        super().__init__(infile, name, rename=True, arch=arch, target=target)
    def core(self,nelight):
        nelight.config.sw_pipelining.enabled = True
        nelight.config.sw_pipelining.minimize_overlapping=False
        nelight.config.reserved_regs = [f"x{i}" for i in range(0,7)] + ["v8", "x30", "sp"]
        nelight.config.inputs_are_outputs = True
        nelight.config.constraints.stalls_first_attempt = 110
        nelight.optimize_loop("layer123_start")

        nelight.config.reserved_regs = ["x3", "x30", "sp"]
        nelight.config.constraints.stalls_first_attempt = 40
        nelight.optimize_loop("layer45678_start")


class ntt_dilithium_123(Example):
    def __init__(self, var="", arch=AArch64_Neon, target=Target_CortexA55):
        name = "ntt_dilithium_123"
        infile = "ntt_dilithium_123_45678"

        if var != "":
            name += f"_{var}"
            infile += f"_{var}"
        name += f"_{target_label_dict[target]}"

        super().__init__(infile, name, rename=True, arch=arch, target=target)

    def core(self, nelight):
        nelight.config.sw_pipelining.enabled = True
        nelight.config.inputs_are_outputs = True
        nelight.config.sw_pipelining.minimize_overlapping = False
        nelight.config.sw_pipelining.optimize_preamble = False
        nelight.config.sw_pipelining.optimize_postamble = False
        nelight.config.reserved_regs = [f"x{i}" for i in range(0, 7)] + ["v8", "x30", "sp"]
        nelight.optimize_loop("layer123_start")


class ntt_dilithium_45678(Example):
    def __init__(self, var="", arch=AArch64_Neon, target=Target_CortexA55):
        name = "ntt_dilithium_45678"
        infile = "ntt_dilithium_123_45678"

        if var != "":
            name += f"_{var}"
            infile += f"_{var}"
        name += f"_{target_label_dict[target]}"

        super().__init__(infile, name, rename=True, arch=arch, target=target)

    def core(self, nelight):
        nelight.config.sw_pipelining.enabled = True
        nelight.config.inputs_are_outputs = True
        nelight.config.sw_pipelining.minimize_overlapping = False
        nelight.config.sw_pipelining.optimize_preamble = False
        nelight.config.sw_pipelining.optimize_postamble = False
        nelight.config.reserved_regs = ["x3", "x30", "sp"]
        nelight.optimize_loop("layer45678_start")


class ntt_dilithium_1234_5678(Example):
    def __init__(self, var="", arch=AArch64_Neon, target=Target_CortexA72):
        name = f"ntt_dilithium_1234_5678"
        infile = name

        if var != "":
            name += f"_{var}"
            infile += f"_{var}"
        name += f"_{target_label_dict[target]}"

        super().__init__(infile, name, rename=True, arch=arch, target=target)

    def core(self, nelight):
        nelight.config.sw_pipelining.enabled = True
        nelight.config.sw_pipelining.minimize_overlapping = False
        nelight.config.reserved_regs = [f"x{i}" for i in range(0, 6)] + ["x30", "sp"]
        nelight.config.inputs_are_outputs = True
        # nelight.config.sw_pipelining.halving_heuristic = True
        # nelight.config.split_heuristic = True
        # nelight.config.split_heuristic_factor = 2
        # nelight.config.split_heuristic_repeat = 4
        # nelight.config.split_heuristic_stepsize = 0.1
        nelight.config.constraints.stalls_first_attempt = 40
        nelight.optimize_loop("layer1234_start")
        nelight.config.reserved_regs = ["x3", "x30", "sp"]
        nelight.config.sw_pipelining.halving_heuristic = False
        nelight.config.split_heuristic = False
        nelight.optimize_loop("layer5678_start")


class ntt_dilithium_1234(Example):
    def __init__(self, var="", arch=AArch64_Neon, target=Target_CortexA72):
        name = "ntt_dilithium_1234"
        infile = "ntt_dilithium_1234_5678"

        if var != "":
            name += f"_{var}"
            infile += f"_{var}"
        name += f"_{target_label_dict[target]}"

        super().__init__(infile, name, rename=True, arch=arch, target=target)

    def core(self, nelight):
        nelight.config.sw_pipelining.enabled = True
        nelight.config.inputs_are_outputs = True
        nelight.config.sw_pipelining.minimize_overlapping = False
        nelight.config.sw_pipelining.optimize_preamble = False
        nelight.config.sw_pipelining.optimize_postamble = False
        nelight.config.reserved_regs = [f"x{i}" for i in range(0, 6)] + ["x30", "sp"]
        nelight.optimize_loop("layer1234_start")


class ntt_dilithium_5678(Example):
    def __init__(self, var="", arch=AArch64_Neon, target=Target_CortexA72):
        name = "ntt_dilithium_5678"
        infile = "ntt_dilithium_1234_5678"

        if var != "":
            name += f"_{var}"
            infile += f"_{var}"
        name += f"_{target_label_dict[target]}"

        super().__init__(infile, name, rename=True, arch=arch, target=target)

    def core(self, nelight):
        nelight.config.sw_pipelining.enabled = True
        nelight.config.inputs_are_outputs = True
        nelight.config.sw_pipelining.minimize_overlapping = False
        nelight.config.sw_pipelining.optimize_preamble = False
        nelight.config.sw_pipelining.optimize_postamble = False
        nelight.config.reserved_regs = ["x3", "x30", "sp"]
        nelight.optimize_loop("layer5678_start")


class intt_dilithium_12_34_56_78(Example):
    def __init__(self):
        super().__init__("intt_dilithium_12_34_56_78", rename=True)
    def core(self,helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.typing_hints = {
            "root0"         : Arch_Armv81M.RegisterType.GPR,
            "root1"         : Arch_Armv81M.RegisterType.GPR,
            "root2"         : Arch_Armv81M.RegisterType.GPR,
            "root0_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root1_twisted" : Arch_Armv81M.RegisterType.GPR,
            "root2_twisted" : Arch_Armv81M.RegisterType.GPR,
        }
        helight.optimize_loop("layer12_loop")
        helight.optimize_loop("layer34_loop")
        helight.optimize_loop("layer56_loop")
        helight.config.typing_hints = {}
        helight.optimize_loop("layer78_loop")

class complex_radix4_fft(Example):
    def __init__(self):
        super().__init__("complex_radix4_fft")
    def core(self,helight):
        helight.config.sw_pipelining.enabled = True
        helight.optimize()

class fixedpoint_radix4_fft(Example):
    def __init__(self, var, symbolic=False):
        self.var = var
        if symbolic:
            sym = "_symbolic"
        else:
            sym = ""
        super().__init__(f"fixedpoint_radix4_fft{sym}_{var}")
    def core(self,helight):
        helight.config.constraints.stalls_first_attempt = 8
        helight.config.sw_pipelining.enabled = True
        if self.var == "preonly":
            helight.config.sw_pipelining.allow_pre  = True
            helight.config.sw_pipelining.allow_post = False
        elif self.var == "postonly":
            helight.config.sw_pipelining.allow_post = True
            helight.config.sw_pipelining.allow_pre  = False
            helight.optimize_loop("fixedpoint_radix4_fft_loop_start")

class q_fft_radix4(Example):
    def __init__(self):
        super().__init__("q_fft_radix4")
    def core(self,helight):
        helight.config.sw_pipelining.enabled = True
        helight.optimize_loop("loop_start")


class fft_fixedpoint_radix4(Example):
    def __init__(self, var="", arch=Arch_Armv81M, target=Target_CortexM55r1):
        name = "fixedpoint_radix4_fft"
        subpath = "fx_r4_fft/"
        infile = subpath + "base_symbolic"
        outfile = subpath + name

        if var != "":
            name += f"_{var}"
            infile += f"_{var}"
        name += f"_{target_label_dict[target]}"

        super().__init__(infile, name, outfile=outfile, rename=True, arch=arch, target=target)

    def core(self, helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.inputs_are_outputs = True
        helight.config.sw_pipelining.minimize_overlapping = False
        helight.config.sw_pipelining.optimize_preamble = False
        helight.config.sw_pipelining.optimize_postamble = False
        helight.optimize_loop("fixedpoint_radix4_fft_loop_start")


class fft_floatingpoint_radix4(Example):
    def __init__(self, var="", arch=Arch_Armv81M, target=Target_CortexM55r1):
        name = "floatingpoint_radix4_fft"
        subpath = "flt_r4_fft/"
        infile = subpath + "base_symbolic"
        outfile = subpath + name

        if var != "":
            name += f"_{var}"
            infile += f"_{var}"
        name += f"_{target_label_dict[target]}"

        super().__init__(infile, name, outfile=outfile, rename=True, arch=arch, target=target)

    def core(self, helight):
        helight.config.sw_pipelining.enabled = True
        # helight.config.inputs_are_outputs = True
        helight.config.sw_pipelining.minimize_overlapping = False
        helight.config.sw_pipelining.optimize_preamble = False
        helight.config.sw_pipelining.optimize_postamble = False
        helight.optimize_loop("flt_radix4_fft_loop_start")

class vmovs(Example):
    def __init__(self, var): # int, mul, double
        super().__init__(f"vmov_{var}")

class vqdmlsdh_vqdmladhx(Example):
    def __init__(self):
        super().__init__(f"vqdmlsdh_vqdmladhx")
    def core(self,helight):
        helight.config.sw_pipelining.enabled = True
        helight.config.typing_hints = { x : Arch_Armv81M.RegisterType.MVE for x in
                                        [ "a", "b", "c", "d", "e", "f" ] }

#############################################################################################

def main():
    examples = [ Example0(),
                 Example1(),
                 Example2(),
                 Example3(),
#                 SBCSample(),
                 CRT(),
                 ntt_n256_l6_s32("bar"),
                 ntt_n256_l6_s32("mont"),
                 ntt_n256_l8_s32("bar"),
                 ntt_n256_l8_s32("mont"),
                 intt_n256_l6_s32("bar"),
                 intt_n256_l6_s32("mont"),
                 intt_n256_l8_s32("bar"),
                 intt_n256_l8_s32("mont"),
                 # Kyber NTT
                 # m55
                 ntt_kyber_1_23_45_67(),
                 ntt_kyber_1_23_45_67(var="no_trans"),
                 ntt_kyber_1_23_45_67(var="no_trans_vld4"),
                 ntt_kyber_12_345_67(False),
                 ntt_kyber_12_345_67(True),
                 # m85
                 ntt_kyber_1_23_45_67(target=Target_CortexM85r1),
                 ntt_kyber_1_23_45_67(var="no_trans", target=Target_CortexM85r1),
                 ntt_kyber_1_23_45_67(var="no_trans_vld4", target=Target_CortexM85r1),
                 ntt_kyber_12_345_67(False, target=Target_CortexM85r1),
                 ntt_kyber_12_345_67(True, target=Target_CortexM85r1),
                 ntt_kyber_l345_symbolic(),
                 # a55
                 ntt_kyber_123_4567(),
                 ntt_kyber_123_4567(var="scalar_load"),
                 ntt_kyber_123_4567(var="scalar_store"),
                 ntt_kyber_123_4567(var="scalar_load_store"),
                 ntt_kyber_123_4567(var="manual_st4"),
                 ntt_kyber_1234_567(),
                 # a72
                 ntt_kyber_123_4567(target=Target_CortexA72),
                 ntt_kyber_123_4567(var="scalar_load", target=Target_CortexA72),
                 ntt_kyber_123_4567(var="scalar_store", target=Target_CortexA72),
                 ntt_kyber_123_4567(var="scalar_load_store", target=Target_CortexA72),
                 ntt_kyber_123_4567(var="manual_st4", target=Target_CortexA72),
                 ntt_kyber_1234_567(target=Target_CortexA72),
                 intt_kyber_1_23_45_67(),
                 # Dilithium NTT
                 # m55
                 ntt_dilithium_12_34_56_78(),
                 ntt_dilithium_12_34_56_78(var="no_trans_vld4"),
                 ntt_dilithium_123_456_78(False),
                 ntt_dilithium_123_456_78(True),
                 # m85
                 ntt_dilithium_12_34_56_78(target=Target_CortexM85r1),
                 ntt_dilithium_12_34_56_78(var="no_trans_vld4", target=Target_CortexM85r1),
                 ntt_dilithium_123_456_78(False, target=Target_CortexM85r1),
                 ntt_dilithium_123_456_78(True, target=Target_CortexM85r1),
                 ntt_dilithium_123_456_78_symbolic(),
                 # a55
                 ntt_dilithium_123_45678(),
                 ntt_dilithium_123_45678(var="w_scalar"),
                 ntt_dilithium_123_45678(var="manual_st4"),
                 ntt_dilithium_1234_5678(),
                 ntt_dilithium_1234_5678(var="manual_st4"),
                 # a72
                 ntt_dilithium_123_45678(target=Target_CortexA72),
                 ntt_dilithium_123_45678(var="w_scalar", target=Target_CortexA72),
                 ntt_dilithium_123_45678(var="manual_st4", target=Target_CortexA72),
                 ntt_dilithium_1234_5678(target=Target_CortexA72),
                 ntt_dilithium_1234_5678(var="manual_st4", target=Target_CortexA72),
                 intt_dilithium_12_34_56_78(),
                 complex_radix4_fft(),
                 fixedpoint_radix4_fft("preonly"),
                 fixedpoint_radix4_fft("postonly"),
                 q_fft_radix4(),
                 vmovs("int"),
                 vmovs("mul"),
                 vmovs("double"),
                 vqdmlsdh_vqdmladhx(),
                ]

    all_example_names = [ e.name for e in examples ]

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--examples", type=str, default="all",
                        help=f"The list of examples to be run, comma-separated list from {all_example_names}. \
                        Format: {{name}}_{{variant}}_{{target}}, e.g., ntt_kyber_123_4567_scalar_load_a55")
    parser.add_argument("--debug", default=False, action="store_true")
    parser.add_argument("--iterations", type=int, default=1)

    args = parser.parse_args()
    if args.examples != "all":
        todo = args.examples.split(",")
    else:
        todo = all_example_names
    iterations = args.iterations

    def run_example(name, debug=False):
        ex = None
        for e in examples:
            if e.name == name:
                ex = e
                break
        if ex == None:
            raise Exception(f"Could not find example {name}")
        ex.run(debug=debug)

    for e in todo:
        for _ in range(iterations):
            run_example(e, debug=args.debug)

if __name__ == "__main__":
   main()
