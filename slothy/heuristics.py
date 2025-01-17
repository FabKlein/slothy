
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

import logging, copy, math, random

from types import SimpleNamespace

from slothy.dataflow import DataFlowGraph as DFG
from slothy.dataflow import Config as DFGConfig
from slothy.core import SlothyBase, Config, Result
from slothy.helper import AsmAllocation, AsmMacro, AsmHelper
from slothy.helper import binary_search, BinarySearchLimitException

class Heuristics():

    def optimize_binsearch_core(source, logger, conf, **kwargs):
        """Shim wrapper around Slothy performing a binary search for the
        minimization of stalls"""

        logger_name = logger.name.replace(".","_")
        last_successful = None

        def try_with_stalls(stalls, timeout=None):
            nonlocal last_successful

            logger.info(f"Attempt optimization with max {stalls} stalls...")
            c = conf.copy()
            c.constraints.stalls_allowed = stalls

            if c.hints.ext_bsearch_remember_successes:
                c.hints.rename_hint_orig_rename = True
                c.hints.order_hint_orig_order = True

            if timeout is not None:
                c.timeout = timeout
            core = SlothyBase(conf.Arch, conf.Target, logger=logger, config=c)

            if last_successful is not None:
                src = last_successful
            else:
                src = source
            success = core.optimize(src, **kwargs)

            if success and c.hints.ext_bsearch_remember_successes:
                last_successful = core.result.code

            return success, core

        try:
            return binary_search(try_with_stalls,
                                 minimum= conf.constraints.stalls_minimum_attempt - 1,
                                 start=conf.constraints.stalls_first_attempt,
                                 threshold=conf.constraints.stalls_maximum_attempt,
                                 precision=conf.constraints.stalls_precision,
                                 timeout_below_precision=conf.constraints.stalls_timeout_below_precision)
        except BinarySearchLimitException:
            logger.error("Exceeded stall limit without finding a working solution")
            logger.error("Here's what you asked me to optimize:")
            Heuristics._dump("Original source code", source, logger=logger, err=True, no_comments=True)
            logger.error("Configuration")
            conf.log(logger.error)

            err_file = self.config.log_dir + f"/{logger_name}_ERROR.s"
            f = open(err_file, "w")
            conf.log(lambda l: f.write("// " + l + "\n"))
            f.write('\n'.join(source))
            f.close()
            self.logger.error(f"Stored this information in {err_file}")

    def optimize_binsearch(source, logger, conf, **kwargs):
        if conf.variable_size:
            return Heuristics.optimize_binsearch_internal(source, logger, conf, **kwargs)
        else:
            return Heuristics.optimize_binsearch_external(source, logger, conf, **kwargs)

    def optimize_binsearch_external(source, logger, conf, flexible=True, **kwargs):
        """Find minimum number of stalls without objective, then optimize
        the objective for a fixed number of stalls."""

        if not flexible:
            core = SlothyBase(conf.Arch, conf.Target, logger=logger,config=conf)
            if not core.optimize(source):
                raise Exception("Optimization failed")
            return core.result

        logger.info(f"Perform binary search for minimal number of stalls...")

        c = conf.copy()
        c.ignore_objective = True
        min_stalls, core = Heuristics.optimize_binsearch_core(source, logger, c, **kwargs)

        if not conf.has_objective:
            return core.result

        logger.info(f"Optimize again with minimal number of {min_stalls} stalls, with objective...")
        first_result = core.result

        core.config.ignore_objective = False
        success = core.retry()

        if not success:
            logger.warning("Re-optimization with objective at minimum number of stalls failed -- should not happen? Will just pick previous result...")
            return first_result

        # core = SlothyBase(conf.Arch, conf.Target, logger=logger, config=c)
        # success = core.optimize(source, **kwargs)
        return core.result

    def optimize_binsearch_internal(source, logger, conf, **kwargs):
        """Find minimum number of stalls without objective, then optimize
        the objective for a fixed number of stalls."""

        logger.info(f"Perform binary search for minimal number of stalls...")

        start_attempt = conf.constraints.stalls_first_attempt
        cur_attempt = start_attempt

        while True:
            c = conf.copy()
            c.variable_size = True
            c.constraints.stalls_allowed = cur_attempt

            logger.info(f"Attempt optimization with max {cur_attempt} stalls...")

            core = SlothyBase(c.Arch, c.Target, logger=logger, config=c)
            success = core.optimize(source, **kwargs)

            if success:
                min_stalls = core.result.stalls
                break

            cur_attempt = max(1,cur_attempt * 2)
            if cur_attempt > conf.constraints.stalls_maximum_attempt:
                logger.error("Exceeded stall limit without finding a working solution")
                raise Exception("No solution found")

        logger.info(f"Minimum number of stalls: {min_stalls}")

        if not conf.has_objective:
            return core.result

        logger.info(f"Optimize again with minimal number of {min_stalls} stalls, with objective...")
        first_result = core.result

        c = conf.copy()
        c.variable_size = False
        c.constraints.stalls_allowed = min_stalls
        core = SlothyBase(c.Arch, c.Target, logger=logger, config=c)
        success = core.optimize(source, retry=True, **kwargs)

        if not success:
            logger.warning("Re-optimization with objective at minimum number of stalls failed -- should not happen? Will just pick previous result...")
            return first_result

        return core.result

    def periodic(body, logger, conf):
        """Heuristics for the optimization of large loops

        Can be called if software pipelining is disabled. In this case, it just
        forwards to the linear heuristic."""

        if conf.sw_pipelining.enabled and not conf.inputs_are_outputs:
            logger.warning("You are using SW pipelining without setting inputs_are_outputs=True. This means that the last iteration of the loop may overwrite inputs to the loop (such as address registers), unless they are marked as reserved registers. If this is intended, ignore this warning. Otherwise, consider setting inputs_are_outputs=True to ensure that nothing that is used as an input to the loop is overwritten, not even in the last iteration.")

        def unroll(source):
            if conf.sw_pipelining.enabled:
                source = source * conf.sw_pipelining.unroll
            source = '\n'.join(source)
            return source

        body = unroll(body)

        if conf.inputs_are_outputs:
            dfg = DFG(body, logger.getChild("dfg_generate_outputs"),
                      DFGConfig(conf.copy()))
            conf.outputs = dfg.outputs
            conf.inputs_are_outputs = False

        # If we're not asked to do software pipelining, just forward to
        # the heurstics for linear optimization.
        if not conf.sw_pipelining.enabled:
            core = Heuristics.linear( body, logger=logger, conf=conf)
            return [], core, [], 0

        if conf.sw_pipelining.halving_heuristic:
            return Heuristics._periodic_halving( body, logger, conf)

        # 'Normal' software pipelining
        #
        # We first perform the core periodic optimization of the loop kernel,
        # and then separate passes for the optimization for the preamble and postamble

        # First step: Optimize loop kernel

        logger.info("Optimize loop kernel...")
        c = conf.copy()
        c.inputs_are_outputs = True
        result = Heuristics.optimize_binsearch(body,logger.getChild("slothy"),c)

        num_exceptional_iterations = result.num_exceptional_iterations
        kernel = result.code

        # Second step: Separately optimize preamble and postamble

        preamble = result.preamble
        if conf.sw_pipelining.optimize_preamble:
            logger.debug("Optimize preamble...")
            Heuristics._dump("Preamble", preamble, logger)
            logger.debug(f"Dependencies within kernel: "\
                         f"{result.kernel_input_output}")
            c = conf.copy()
            c.outputs = result.kernel_input_output
            c.sw_pipelining.enabled=False
            preamble = Heuristics.linear(preamble,conf=c, logger=logger.getChild("preamble"))

        postamble = result.postamble
        if conf.sw_pipelining.optimize_postamble:
            logger.debug("Optimize postamble...")
            Heuristics._dump("Preamble", postamble, logger)
            c = conf.copy()
            c.sw_pipelining.enabled=False
            postamble = Heuristics.linear(postamble, conf=c, logger=logger.getChild("postamble"))

        return preamble, kernel, postamble, num_exceptional_iterations

    def linear(body, logger, conf, visualize_stalls=True):
        """Heuristic for the optimization of large linear chunks of code.

        Must only be called if software pipelining is disabled."""
        if conf.sw_pipelining.enabled:
            raise Exception("Linear heuristic should only be called with SW pipelining disabled")

        Heuristics._dump("Starting linear optimization...", body, logger)

        # So far, we only implement one heuristic: The splitting heuristic --
        # If that's disabled, just forward to the core optimization
        if not conf.split_heuristic:
            result = Heuristics.optimize_binsearch(body,logger.getChild("slothy"), conf)
            return result.code

        return Heuristics._split( body, logger, conf, visualize_stalls)

    def _naive_reordering(body, logger, conf):
        logger.info("Perform naive interleaving by depth... ")
        old = body.copy()
        l = len(body)
        dfg = DFG(body, logger.getChild("dfg"), DFGConfig(conf.copy()), parsing_cb=True)
        depths = [dfg.nodes_by_id[i].depth for i in range(l) ]
        insts = [dfg.nodes[i].inst for i in range(l)]

        last_unit = None

        for i in range(l):
            def get_inputs(inst):
                return set(inst.args_in + inst.args_in_out)
            def get_outputs(inst):
                return set(inst.args_out + inst.args_in_out)

            joint_prev_inputs = {}
            joint_prev_outputs = {}
            cur_joint_prev_inputs = set()
            cur_joint_prev_outputs = set()
            for j in range(i,l):
                joint_prev_inputs[j] = cur_joint_prev_inputs
                cur_joint_prev_inputs = cur_joint_prev_inputs.union(get_inputs(insts[j]))

                joint_prev_outputs[j] = cur_joint_prev_outputs
                cur_joint_prev_outputs = cur_joint_prev_outputs.union(get_outputs(insts[j]))

            # Find instructions which could, in principle, come next, without
            # any renaming
            def could_come_next(j):
                cur_outputs = get_outputs(insts[j])
                prev_inputs = joint_prev_inputs[j]

                cur_inputs = get_inputs(insts[j])
                prev_outputs = joint_prev_outputs[j]

                ok =     len(cur_outputs.intersection(prev_inputs)) == 0 \
                    and  len(cur_inputs.intersection(prev_outputs)) == 0

                return ok
            candidate_idxs = list(filter(could_come_next, range(i,l)))
            logger.debug(f"Potential next candidates: {candidate_idxs}")

            # print("CANDIDATES: " + '\n* '.join(list(map(lambda idx: str((body[idx], conf.Target.get_units(insts[idx]))), candidate_idxs))))
            # There a different strategies one can pursue here, some being:
            # - Always pick the candidate instruction of the smallest depth
            # - Peek into the uArch model and try to alternate between functional units
            #   It's a bit disappointing if this is necessary, since SLOTHY should do this.
            #   However, running it on really large snippets (1000 instructions) remains
            #   infeasible, even if latencies and renaming are disabled.

            strategy = "minimal_depth"
            # strategy = "alternate_functional_units"

            if strategy == "minimal_depth":

                 candidate_depths = list(map(lambda j: depths[j], candidate_idxs))
                 logger.debug(f"Candidate depths: {candidate_depths}")
                 choice_idx = candidate_idxs[candidate_depths.index(min(candidate_depths))]

            elif strategy == "alternate_functional_units":

                def flatten_units(units):
                    res = []
                    for u in units:
                        if isinstance(u,list):
                            res += u
                        else:
                            res.append(u)
                    return res
                def units_disjoint(a,b):
                    if a is None or b is None:
                        return True
                    a = flatten_units(a)
                    b = flatten_units(b)
                    return len([x for x in a if x in b]) == 0
                def units_different(a,b):
                    return a != b

                disjoint_unit_idxs = [ i for i in candidate_idxs if units_disjoint(conf.Target.get_units(insts[i]), last_unit) ]
                other_unit_idxs = [ i for i in candidate_idxs if units_different(conf.Target.get_units(insts[i]), last_unit) ]

                # print("FROM DISJOINT UNITS: " + '\n* '.join(list(map(lambda idx: body[idx], disjoint_unit_idxs))))
                # print("FROM OTHER UNITS: " + '\n* '.join(list(map(lambda idx: body[idx], other_unit_idxs))))

                if len(disjoint_unit_idxs) > 0:
                    choice_idx = random.choice(disjoint_unit_idxs)
                    last_unit = conf.Target.get_units(insts[choice_idx])
                elif len(other_unit_idxs) > 0:
                    choice_idx = random.choice(other_unit_idxs)
                    last_unit = conf.Target.get_units(insts[choice_idx])
                else:
                    candidate_depths = list(map(lambda j: depths[j], candidate_idxs))
                    logger.debug(f"Candidate depths: {candidate_depths}")
                    min_depth = min(candidate_depths)
                    refined_candidates = [ candidate_idxs[i] for i,d in enumerate(candidate_depths) if d == min_depth ]
                    choice_idx = random.choice(refined_candidates)

            else:
                raise Exception("Unknown preprocessing strategy")

            choice_inst = insts[choice_idx]

#            print(f"INSTRUCTION: {body[choice_idx]}")
#            logger.debug(f"Pick instruction: {body[choice_idx]}")

            def move_entry_forward(lst, idx_from, idx_to):
                entry = lst[idx_from]
                del lst[idx_from]
                return lst[:idx_to] + [entry] + lst[idx_to:]

            body = move_entry_forward(body, choice_idx, i)
            insts = move_entry_forward(insts, choice_idx, i)
            depths = move_entry_forward(depths, choice_idx, i)

            body[i] = f"    {body[i].strip():100s} // depth {depths[i]}"

            Heuristics._dump(f"New code", body, logger)

        Heuristics._dump(f"Before naive interleaving", old, logger)
        Heuristics._dump(f"After naive interleaving", body, logger)
        return body

    def _idxs_from_fractions(fraction_lst, body):
        return [ round(f * len(body)) for f in fraction_lst ]

    def _split_inner(body, logger, conf, visualize_stalls=True):

        l = len(body)
        if l == 0:
            return body
        log = logger.getChild("split")

        # Allow to proceed in steps
        split_factor = conf.split_heuristic_factor

        def optimize_sequence_of_aligned_chunks(start_idx_lst, body, conf):
            """Splits the input source code into disjoint chunks, delimited by the provided
            index list, and optimizes them separately. Renaming of inputs&outputs allowed."""

            start_idx_lst.sort()
            start_idx_lst.reverse()
            next_end_idx = len(body)
            cur_output = conf.outputs
            cur_output_renaming = copy.copy(conf.rename_outputs)
            new_body = []
            for i, start_idx in enumerate(start_idx_lst):

                i = len(start_idx_lst) - i
                end_idx = next_end_idx

                cur_pre  = body[:start_idx]
                cur_body = body[start_idx:end_idx]
                cur_post = body[end_idx:]

                Heuristics._dump(f"Chunk {i}", cur_body, log)
                Heuristics._dump(f"Cur post {i}", cur_post, log)

                c = conf.copy()
                log.debug("Current output: {cur_output}")
                if i != 1:
                    c.rename_inputs = conf.rename_inputs # c.rename_inputs = { "other" : "any" }
                else:
                    c.rename_inputs = conf.rename_inputs
                c.rename_outputs = cur_output_renaming
                c.inputs_are_outputs = False
                c.outputs = cur_output
                result = Heuristics.optimize_binsearch(cur_body,
                                                       log.getChild(f"{i-1}_{len(start_idx_lst)}"), c)
                new_body = result.code + new_body
                Heuristics._dump(f"New chunk {i}", result.code, log)

                cur_output = result.orig_inputs.copy()
                cur_output_renaming = result.input_renamings.copy()

                next_end_idx = start_idx

            return new_body

        # # First, let's make sure that everything's written without symbolic registers
        # log.debug("Functional-only optimization to remove symbolics...")
        # c = conf.copy()
        # c.constraints.allow_reordering = False
        # c.constraints.functional_only = True
        # body = optimize_sequence_of_aligned_chunks(Heuristics._idxs_from_fractions([0,0.3,0.7], body), body, c)
        # body = AsmHelper.reduce_source(body)

        # res = Result(c)
        # res._orig_code = body
        # res._codesize = len(body)
        # res._code = body
        # res._success = True
        # res._reordering = {i:i for i in range(len(body))}
        # res._reordering_inv = {i:i for i in range(len(body))}
        # res._reordering_with_bubbles = {i:i for i in range(len(body))}
        # res._reordering_with_bubbles_inv = {i:i for i in range(len(body))}
        # res._input_renamings = { t : t for t in c.outputs }
        # res._output_renamings = { t : t for t in c.outputs }
        # SlothyBase._selfcheck(res, log)
        # print(f" OUTPUTS: {c.outputs}")

        # Heuristics._dump("Source code without symbolic registers", body, log)

        if conf.split_heuristic_preprocess_naive_interleaving:
            body = Heuristics._naive_reordering(body, log, conf)

        # conf.outputs = result.outputs

        def print_intarr(arr, l,vals=50):
            m = max(10,max(arr))
            start_idxs = [ (l * i)     // vals for i in range(vals) ]
            end_idxs   = [ (l * (i+1)) // vals for i in range(vals) ]
            avgs = []
            for (s,e) in zip(start_idxs, end_idxs):
                avg = sum(arr[s:e]) // (e-s)
                avgs.append(avg)
                log.info(f"[{s:3d}-{e:3d}]: {'*'*avg}{'.'*(m-avg)} ({avg})")

        def print_stalls(stalls,l):
            chunk_len = int(l // split_factor)
            # Convert stalls into 01 valued function
            stalls_arr = [ i in stalls for i in range(l) ]
            for v in stalls_arr:
                assert v in {0,1}
            stalls_cumulative = [ sum(stalls_arr[max(0,i-math.floor(chunk_len/2)):i+math.ceil(chunk_len/2)]) for i in range(l) ]
            print_intarr(stalls_cumulative,l)

        def optimize_chunk(start_idx, end_idx, body, stalls,show_stalls=True):
            """Optimizes a sub-chunks of the given snippet, delimited by pairs
            of start and end indices provided as arguments. Input/output register
            names stay intact -- in particular, overlapping chunks are allowed."""

            cur_pre  = body[:start_idx]
            cur_body = body[start_idx:end_idx]
            cur_post = body[end_idx:]

            if not conf.split_heuristic_optimize_seam:
                prefix_len = 0
                suffix_len = 0
            else:
                prefix_len = min(len(cur_pre), conf.split_heuristic_optimize_seam)
                suffix_len = min(len(cur_post), conf.split_heuristic_optimize_seam)
                cur_prefix = cur_pre[-prefix_len:]
                cur_suffix = cur_post[:suffix_len]
                cur_body = cur_prefix + cur_body + cur_suffix
                cur_pre = cur_pre[:-prefix_len]
                cur_post = cur_post[suffix_len:]

            Heuristics._dump(f"Optimizing chunk [{start_idx}-{prefix_len}:{end_idx}+{suffix_len}]", cur_body, log)
            if prefix_len > 0:
                Heuristics._dump(f"Using prefix", cur_prefix, log)
            if suffix_len > 0:
                Heuristics._dump(f"Using suffix", cur_suffix, log)

            # Find dependencies of rest of body

            dfgc = DFGConfig(conf.copy())
            dfgc.outputs = dfgc.outputs.union(conf.outputs)
            cur_outputs = DFG(cur_post, log.getChild("dfg_infer_outputs"),dfgc).inputs

            c = conf.copy()
            c.rename_inputs  = { "other" : "static" } # No renaming
            c.rename_outputs = { "other" : "static" } # No renaming
            c.inputs_are_outputs = False
            c.outputs = cur_outputs

            result = Heuristics.optimize_binsearch(cur_body,
                                                   log.getChild(f"{start_idx}_{end_idx}"),
                                                   c,
                                                   prefix_len=prefix_len,
                                                   suffix_len=suffix_len)
            Heuristics._dump(f"New chunk [{start_idx}:{end_idx}]", result.code, log)
            new_body = cur_pre + AsmHelper.reduce_source(result.code) + cur_post

            keep_stalls = { i for i in stalls if i < start_idx - prefix_len or i >= end_idx + suffix_len }
            new_stalls = keep_stalls.union(map(lambda i: i + start_idx - prefix_len, result.stall_positions))

            if show_stalls:
                print_stalls(new_stalls,l)

            return new_body, new_stalls, len(result.stall_positions)

        def optimize_chunks_many(start_end_idx_lst, body, stalls, abort_stall_threshold=None, **kwargs):
            for start_idx, end_idx in start_end_idx_lst:
                body, stalls, cur_stalls = optimize_chunk(start_idx, end_idx, body, stalls, **kwargs)
                if abort_stall_threshold is not None and cur_stalls > abort_stall_threshold:
                    break
            return body, stalls

        cur_body = body

        def make_idx_list_consecutive(factor, increment):
            chunk_len = 1 / factor
            cur_start = 0
            cur_end = 0
            start_pos = []
            end_pos = []
            while cur_end < 1.0:
                cur_end = cur_start + chunk_len
                if cur_end > 1.0:
                    cur_end = 1.0
                start_pos.append(cur_start)
                end_pos.append(cur_end)

                cur_start += increment

            def not_empty(x):
                return x[0] != x[1]
            idx_lst = zip(Heuristics._idxs_from_fractions(start_pos, cur_body),
                          Heuristics._idxs_from_fractions(end_pos, cur_body))
            idx_lst = list(filter(not_empty, idx_lst))
            return idx_lst

        stalls = set()
        increment = 1 / split_factor

        # First, do a 'dry run' solely for finding the initial 'stall map'
        if conf.split_heuristic_repeat > 0:
            orig_conf = conf.copy()
            conf.constraints.allow_reordering = False
            conf.constraints.allow_renaming = False
            idx_lst = make_idx_list_consecutive(split_factor, increment)
            cur_body, stalls = optimize_chunks_many(idx_lst, cur_body, stalls,show_stalls=False)
            conf = orig_conf.copy()

            log.info("Initial stalls")
            print_stalls(stalls,l)

        if conf.split_heuristic_stepsize is None:
            increment = 1 / (2*split_factor)
        else:
            increment = conf.split_heuristic_stepsize

        for _ in range(conf.split_heuristic_repeat):

            cur_body = AsmHelper.reduce_source(cur_body)

            if not conf.split_heuristic_random:
                idx_lst = make_idx_list_consecutive(split_factor, increment)
                if conf.split_heuristic_bottom_to_top == True:
                    idx_lst.reverse()
            elif conf.split_heuristic_chunks:
                start_pos = [ fst(x) for x in conf.split_heuristic_chunks ]
                end_pos   = [ snd(x) for x in conf.split_heuristic_chunks ]
                idx_lst = zip(Heuristics._idxs_from_fractions(start_pos, cur_body),
                              Heuristics._idxs_from_fractions(end_pos, cur_body))
                idx_lst = list(filter(not_empty, idx_lst))
            else:
                len_total = len(cur_body)
                len_chunk = round(len_total / split_factor)
                start_idx = random.randint(0, len_total - len_chunk - 1)
                end_idx = start_idx + len_chunk
                idx_lst = [ (start_idx, end_idx) ]

            cur_body, stalls = optimize_chunks_many(idx_lst, cur_body, stalls,
                                                    abort_stall_threshold=conf.split_heuristic_abort_cycle_at)

        maxlen = max([len(s) for s in cur_body])
        for i in stalls:
            if i > len(cur_body):
                log.error(f"Something is wrong: Index {i}, body length {len(cur_body)}")
                Heuristics._dump(f"Body:", cur_body, log, err=True)
            cur_body[i] = f"{cur_body[i]:{maxlen+8}s} // gap(s) to follow"

        # Visualize model violations
        if conf.split_heuristic_visualize_stalls:
            cur_body = AsmHelper.reduce_source(cur_body)
            c = conf.copy()
            c.constraints.allow_reordering = False
            c.constraints.allow_renaming = False
            c.visualize_reordering = False
            cur_body = Heuristics.optimize_binsearch( cur_body, log.getChild("visualize_stalls"), c).code
            cur_body = ["// Start split region"] + cur_body + ["// End split region"]

        # Visualize functional units
        if conf.split_heuristic_visualize_units:
            dfg = DFG(cur_body, logger.getChild("visualize_functional_units"), DFGConfig(c))
            new_body = []
            for (l,t) in enumerate(dfg.nodes):
                unit = conf.Target.get_units(t.inst)[0]
                indentation = conf.Target.ExecutionUnit.get_indentation(unit)
                new_body[i] = f"{'':{indentation}s}" + l
            cur_body = new_body

        return cur_body

    def _split(body, logger, conf, visualize_stalls=True):
        c = conf.copy()

        # Focus on the chosen subregion
        body = AsmHelper.reduce_source(body)

        if c.split_heuristic_region == [0.0, 1.0]:
            return Heuristics._split_inner(body, logger, c, visualize_stalls)

        start_end_idxs = Heuristics._idxs_from_fractions(c.split_heuristic_region, body)
        start_idx = start_end_idxs[0]
        end_idx = start_end_idxs[1]

        pre = body[:start_idx]
        cur = body[start_idx:end_idx]
        post = body[end_idx:]

        # Adjust the outputs
        c.outputs = DFG(post, logger.getChild("dfg_generate_outputs"), DFGConfig(c)).inputs
        c.inputs_are_outputs = False

        cur = Heuristics._split_inner(cur, logger, c, visualize_stalls)
        body = pre + cur + post
        return body

    def _dump(name, s, logger, err=False, no_comments=False):
        def strip_comments(sl):
            return [ s.split("//")[0].strip() for s in sl ]

        fun = logger.debug if not err else logger.error
        fun(f"Dump: {name}")
        if isinstance(s, str):
          s = s.splitlines()
        if no_comments:
            s = strip_comments(s)
        for l in s:
            fun(f"> {l}")

    def _periodic_halving(body, logger, conf):

        assert conf != None
        assert conf.sw_pipelining.enabled
        assert conf.sw_pipelining.halving_heuristic

        # Find kernel dependencies
        kernel_deps = DFG(body, logger.getChild("dfg_kernel_deps"),
                          DFGConfig(conf.copy())).inputs

        # First step: Optimize loop kernel, but without software pipelining
        c = conf.copy()
        c.sw_pipelining.enabled = False
        c.inputs_are_outputs = True
        c.outputs = c.outputs.union(kernel_deps)
        kernel = Heuristics.linear(body,logger.getChild("slothy"),conf=c,
                                   visualize_stalls=False)

        #
        # Second step:
        # Optimize the loop body _again_, but  swap the two loop halves to that
        # successive iterations can be interleaved somewhat.
        #
        # The benefit of this approach is that we never call SLOTHY with generic SW pipelining,
        # which is computationally significantly more complex than 'normal' optimization.
        # We do still enable SW pipelining in SLOTHY if `halving_heuristic_periodic` is set, but
        # this is only to make SLOTHY consider the 'seam' between iterations -- since we unset
        # `allow_pre/post`, SLOTHY does not consider any loop interleaving.
        #

        # If the optimized loop body is [A;B], we now optimize [B;A], that is, the late half of one
        # iteration followed by the early half of the successive iteration. The hope is that this
        # enables good interleaving even without calling SLOTHY in SW pipelining mode.

        kernel = AsmHelper.reduce_source(kernel)
        kernel_len  = len(kernel)
        kernel_lenh = kernel_len // 2
        kernel_low  = kernel[:kernel_lenh]
        kernel_high = kernel[kernel_lenh:]
        kernel = kernel_high.copy() + kernel_low.copy()

        preamble, postamble = kernel_low, kernel_high

        dfgc = DFGConfig(conf.copy())
        dfgc.outputs = kernel_deps
        dfgc.inputs_are_outputs = False
        kernel_deps = DFG(kernel_high, logger.getChild("dfg_kernel_deps"),dfgc).inputs

        dfgc = DFGConfig(conf.copy())
        dfgc.inputs_are_outputs = True
        kernel_deps = DFG(kernel, logger.getChild("dfg_kernel_deps"),dfgc).inputs

        logger.info("Apply halving heuristic to optimize two halves of consecutive loop kernels...")

        # The 'periodic' version considers the 'seam' between loop iterations; otherwise, we consider
        # [B;A] as a non-periodic snippet, which may still lead to stalls at the loop boundary.

        if conf.sw_pipelining.halving_heuristic_periodic:
            c = conf.copy()
            c.inputs_are_outputs = True
            c.sw_pipelining.minimize_overlapping = False
            c.sw_pipelining.enabled=True      # SW pipelining enabled, but ...
            c.sw_pipelining.allow_pre=False   # - no early instructions
            c.sw_pipelining.allow_post=False  # - no late instructions
                                              # Just make sure to consider loop boundary
            kernel = Heuristics.optimize_binsearch( kernel, logger.
                                                    getChild("periodic heuristic"), conf=c).code
        else:
            c = conf.copy()
            c.outputs = kernel_deps
            c.sw_pipelining.enabled=False
            kernel = Heuristics.linear( kernel, logger.getChild("heuristic"), conf=c)

        num_exceptional_iterations = 1
        return preamble, kernel, postamble, num_exceptional_iterations
