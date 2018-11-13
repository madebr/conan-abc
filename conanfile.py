from conans import ConanFile, CMake, tools
import os


class AbcConan(ConanFile):
    name = "abc"
    version = "20181113"
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
        "threads": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threads": True,
    }
    no_copy_source = True
    _source_subfolder = "sources"
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "LICENSE.md"]

    _version_sha1 = {
        "20181113": "866f332c5d1264a316da8882446973103e84567d",
        "20181112": "9a59b2c2efccdeb085dc53ded7fe8bfcb01e8f2c",
        "20181023": "455e0bae3e1b40a1777b5f3103bff26b6bcefac3",
    }
    # _scm_url = "https://github.com/berkeley-abc/abc.git"
    _scm_url = "https://github.com/madebr/abc.git"

    @property
    def _has_readline(self):
        return self.settings.os != "Windows" or self.settings.compiler != "Visual Studio"

    def requirements(self):
        if self._has_readline:
            self.requires("readline/7.0@bincrafters/stable")
        if self.options.threads:
            if self.settings.compiler == "Visual Studio":
                self.requires("pthread-win32/2.9.1@bincrafters/stable")

    def source(self):
        branch = None
        if self.version.startswith("branch-"):
            _, _, branch = self.version.partition("branch-")
        gitdir = os.path.join(self.source_folder, self._source_subfolder)
        git = tools.Git(folder=gitdir)
        git.clone(self._scm_url, branch=branch if branch is not None else "master")
        if branch is None:
            sha1 = self._version_sha1[self.version]
            git.checkout(sha1)

    def _create_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["ABC_USE_NO_READLINE"] = not self._has_readline
        cmake.definitions["ABC_USE_PIC"] = self.options.shared or self.options.fPIC
        cmake.definitions["ABC_USE_NO_PTHREADS"] = not self.options.threads
        if self.settings.compiler == "Visual Studio":
            cmake.definitions["ABC_USE_EXTERNAL_PTHREAD"] = True
        return cmake

    def build(self):
        cmake = self._create_cmake()
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = self._create_cmake()
        cmake.install()
        self.copy("*.h", dst="include", src=os.path.join(self.source_folder, self._source_subfolder, "src"))
        self.copy("LICENSE.md", dst="licenses")

    def package_info(self):
        abc_bin = next(x for x in os.listdir(os.path.join(self.package_folder, "bin")) if os.path.basename(x).startswith("abc"))
        self.env_info.ABC_BIN = abc_bin
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libdirs = ["lib"]
        libs = tools.collect_libs(self)
        if self.settings.compiler != "Visual Studio":
            if self.options.threads:
                libs.append("pthread")
            libs.append("m")
        if self.settings.os != "Windows":
            libs.append("dl")
        self.cpp_info.libs = libs
