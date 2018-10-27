from conans import ConanFile, CMake, tools
from contextlib import contextmanager
import os


class AbcConan(ConanFile):
    name = "abc"
    version = "20181112"
    description = "System for Sequential Logic Synthesis and Formal Verification"
    topics = ["conan", "abc", "logic", "synthesis", "formal", "verification"]
    url = "https://github.com/bincrafters/conan-abc"
    homepage = "http://www.eecs.berkeley.edu/~alanmi/abc"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    no_copy_source = True
    _source_subfolder = "sources"
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "LICENSE.md"]

    _version_sha1 = {
        "20181112": "9a59b2c2efccdeb085dc53ded7fe8bfcb01e8f2c",
        "20181023": "455e0bae3e1b40a1777b5f3103bff26b6bcefac3",
    }

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("msys2_installer/latest@bincrafters/stable")

    def requirements(self):
        if self.settings.os != "Windows" or self.settings.compiler != "Visual Studio":
            self.requires("readline/7.0@bincrafters/stable")

    def source(self):
        sha1 = self._version_sha1[self.version]
        gitdir = os.path.join(self.source_folder, self._source_subfolder)
        git = tools.Git(folder=gitdir)
        git.clone("https://github.com/berkeley-abc/abc.git", "master")
        git.checkout(sha1)

        cmake_file = os.path.join(gitdir, "CMakeLists.txt")
        tools.replace_in_file(cmake_file,
                              "add_library(libabc EXCLUDE_FROM_ALL ${ABC_SRC})",
                              "add_library(libabc ${ABC_SRC})")
        tools.replace_in_file(cmake_file,
                              "ABC_MAKE_NO_DEPS=1",
                              "ABC_MAKE_NO_DEPS=1 ARCHFLAGS=-DABC_USE_STDINT_H=1")
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "src", "opt", "dau", "dauCanon.c"),
                              "inline void Abc_TtVerifySmallTruth",
                              "void Abc_TtVerifySmallTruth")
        with open(cmake_file, "a") as f:
            f.write("""
install(TARGETS abc libabc
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
)""")

    @contextmanager
    def _create_build_environment(self):
        if self.settings.os == "Windows":
            with tools.environment_append({"PATH": [self.deps_env_info.MSYS_BIN]}):
                yield
        else:
            yield

    def build(self):
        with self._create_build_environment():
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
            cmake.install()

    def package(self):
        self.copy("*.h", dst="include", src=os.path.join(self.source_folder, self._source_subfolder, "src"))
        self.copy("LICENSE.md", dst="licenses")

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libdirs = ["lib"]
        libs = tools.collect_libs(self)
        if self.settings.compiler != "Visual Studio":
            libs.extend(["m",  "pthread", "dl"])
        if self.settings.os != "Macos":
            libs.extend(["rt"])
        self.cpp_info.libs = libs
