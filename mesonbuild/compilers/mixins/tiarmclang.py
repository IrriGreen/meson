# SPDX-License-Identifier: Apache-2.0
# Copyright 2012-2024 The Meson development team

from __future__ import annotations

"""Representations specific to the Texas Instruments Clang compiler family
(ARM-CGT-CLANG)."""

import os
import typing as T

from ...mesonlib import EnvironmentException, OptionKey
from ...linkers.linkers import TIArmClangDynamicLinker
from ..compilers import clike_debug_args
from .clang import clang_color_args, clang_optimization_args

if T.TYPE_CHECKING:
    from ...environment import Environment
    from ...compilers.compilers import Compiler
else:
    # This is a bit clever, for mypy we pretend that these mixins descend from
    # Compiler, so we get all of the methods and attributes defined for us, but
    # for runtime we make them descend from object (which all classes normally
    # do). This gives up DRYer type checking, with no runtime impact
    Compiler = object

class TIArmClangCompiler(Compiler):
    id = 'tiarmclang'

    def __init__(self) -> None:
        if not self.is_cross:
            raise EnvironmentException('TI Arm Clang compiler only supports cross-compilation.')
        if not isinstance(self.linker, TIArmClangDynamicLinker):
            raise EnvironmentException(f'Unsupported Linker {self.linker.exelist}, must be tiarmlnk')
#        self.base_options = {
#            OptionKey(o) for o in
#            ['b_lto', 'b_pgo', 'b_sanitize', 'b_coverage',
#             'b_ndebug', 'b_staticpic', 'b_colorout']}

    def get_pic_args(self) -> T.List[str]:
        return []

    def get_colorout_args(self, colortype: str) -> T.List[str]:
        return clang_color_args[colortype][:]

    def get_pch_suffix(self) -> str:
        return 'pch'

    def get_pch_use_args(self, pch_dir: str, header: str) -> T.List[str]:
        # Workaround for Clang bug http://llvm.org/bugs/show_bug.cgi?id=15136
        # This flag is internal to Clang (or at least not documented on the man page)
        # so it might change semantics at any time.
        return ['-include-pch', os.path.join(pch_dir, self.get_pch_name(header))]

    def get_dependency_gen_args(self, outtarget: str, outfile: str) -> T.List[str]:
        return ['-MD', '-MT', outtarget, '-MF', outfile]

    def get_optimization_args(self, optimization_level: str) -> T.List[str]:
        return clang_optimization_args[optimization_level]

    def get_debug_args(self, is_debug: bool) -> T.List[str]:
        return clike_debug_args[is_debug]

    def compute_parameters_with_absolute_paths(self, parameter_list: T.List[str], build_dir: str) -> T.List[str]:
        for idx, i in enumerate(parameter_list):
            if i[:2] == '-I' or i[:2] == '-L':
                parameter_list[idx] = i[:2] + os.path.normpath(os.path.join(build_dir, i[2:]))

        return parameter_list

    def can_compile(self, src: 'mesonlib.FileOrString') -> bool:
        # XXX - Why can't I do this in __init__()?
        # Assembly
        self.can_compile_suffixes.add('s')
        self.can_compile_suffixes.add('sx')
        return self.can_compile_suffixes
