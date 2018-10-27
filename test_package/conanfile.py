# -*- coding: utf-8 -*-

import os

from conans import ConanFile, CMake, tools


class AbcTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports_sources = ["demo.blif"]

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib*", dst="bin", src="lib")
        self.copy('*.so*', dst='bin', src='lib')

    def test(self):
        bin_path = os.path.join("bin", "test_package")
        cmd = "{} {}".format(bin_path, os.path.join(self.source_folder, "demo.blif"))
        self.run(cmd, run_environment=True)
