#!/usr/bin/env python
import sys
import os
import subprocess
import shutil
import multiprocessing

git = "git"
install_path=""
opm_common = ""
repository_pullrequest_ = {}
working_dir =""


def git_merge_pr(pr):
    subprocess.check_call([git , "pull" , "origin", "master"])
    if pr is not None:
        pr_branch = "PR-" + pr
        fetch_pull_request = "pull/" + pr + "/head:" + pr_branch
        subprocess.check_call([git, "fetch", "origin", fetch_pull_request])
        subprocess.check_call([git, "checkout", pr_branch])
        subprocess.check_call([git, "merge", "master"])


class PathContext(object):
    def __init__(self , path):
        self.cwd = os.getcwd()
        os.chdir( path )

    def __exit__(self , exc_type , exc_val , exc_tb):
        os.chdir( self.cwd )
        return False

    def __enter__(self):
        return self



def build_ert(cmake, ert_build_options):
    if os.path.isdir("build"):
        try:
            shutil.rmtree("build")
        except:
            pass

    os.makedirs("build")
    numcpu = str(multiprocessing.cpu_count())

    with PathContext("build"):
        build_dir = os.getcwd()
        cmake_arglist = [cmake, "../devel"]
        cmake_arglist.extend(ert_build_options)
        subprocess.check_call(cmake_arglist)
        subprocess.check_call(["make",  "-j" , numcpu , "install"], cwd=build_dir)
        subprocess.check_call(["ctest", "--output-on-failure", "-LE", "StatoilData"], cwd=build_dir)




def build_opm(cmake, opm_build_options):
    if os.path.isdir("build"):
        try:
            shutil.rmtree( "build" )
        except:
            pass

    os.makedirs("build")
    numcpu = str(multiprocessing.cpu_count())

    with PathContext("build"):
        build_dir=os.getcwd()
        cmake_arglist = [cmake, "../", "-DOPM_COMMON_ROOT=%s" % opm_common]
        cmake_arglist.extend(opm_build_options)
        subprocess.check_call(cmake_arglist)
        subprocess.check_call(["make", "-j", numcpu, "install"], cwd=build_dir)
        subprocess.check_call(["ctest", "--output-on-failure"])


repo_list = [("ert"              , "git://github.com/Ensembles/ert.git"        , build_ert),
             ("opm-common"       , "git://github.com/OPM/opm-common.git"       , build_opm),
	         ("opm-parser"       , "git://github.com/OPM/opm-parser.git"       , build_opm),
             ("opm-material"     , "git://github.com/OPM/opm-material.git"     , build_opm),
             ("opm-core"         , "git://github.com/OPM/opm-core.git"         , build_opm),
             ("dune-cornerpoint" , "git://github.com/OPM/dune-cornerpoint.git" , build_opm),
             ("opm-autodiff"     , "git://github.com/OPM/opm-autodiff.git"     , build_opm),
             ("opm-porsol"       , "git://github.com/OPM/opm-porsol.git"       , build_opm),
             ("opm-upscaling"    , "git://github.com/OPM/opm-upscaling.git"    , build_opm)]


def cleanup():
    for repo, url, build in repo_list:
    	with PathContext(repo):
	  if repo in repository_pullrequest_:
              pr = repository_pullrequest_[repo]
              if pr is not None:
                  subprocess.check_call([git , "checkout" , "master"])
        	  pr_branch = "PR-" + pr
        	  subprocess.check_call([git , "branch" , "-D", pr_branch])


def multi_pr(args):
    if len(args) == 4:
        path_to_cmake     = args[0]
        install_path      = args[1]
        opm_cmake_options = args[2]
        ert_cmake_options = args[3]
    else:
        print("Wrong number of arguments, arguments are: cmake_path, install_path, [opm_cmake_options], [ert_cmake_options]")
        sys.exit(0)

    cmake = os.path.join(path_to_cmake, "cmake")
    global working_dir
    working_dir = os.getcwd()

    if os.path.exists( install_path ):
        try:
            shutil.rmtree( install_path )
        except Exception:
            sys.stderr.write("** Warning: failed to wipe install directory:%s\n" % install_path)
            sys.exit(1)

    global opm_common
    opm_common = os.path.join(os.getcwd(), "opm-common")



    if "ert" in os.environ:
        repository_pullrequest_["ert"] = os.environ["ert"]
    if "opm-common" in os.environ:
        repository_pullrequest_["opm-common"] = os.environ["opm-common"]
    if "opm-parser" in os.environ:
        repository_pullrequest_["opm-parser"] = os.environ["opm-parser"]
    if "opm-material" in os.environ:
        repository_pullrequest_["opm-material"] = os.environ["opm-material"]
    if "opm-core" in os.environ:
        repository_pullrequest_["opm-core"] = os.environ["opm-core"]
    if "dune-cornerpoint" in os.environ:
        repository_pullrequest_["dune-cornerpoint"] = os.environ["dune-cornerpoint"]
    if "opm-autodiff" in os.environ:
        repository_pullrequest_["opm-autodiff"] = os.environ["opm-autodiff"]
    if "opm-porsol" in os.environ:
        repository_pullrequest_["opm-porsol"] = os.environ["opm-porsol"]
    if "opm-upscaling" in os.environ:
        repository_pullrequest_["opm-upscaling"] = os.environ["opm-upscaling"]




    for repo, url, build in repo_list:
        if not os.path.isdir(repo):
		    subprocess.check_call([ git , "clone" , url])

        with PathContext(repo):
            subprocess.check_call([git , "checkout" , "master"])

            if repo in repository_pullrequest_:
                pr = repository_pullrequest_[repo]
                git_merge_pr(pr)
            else:
                subprocess.check_call([git , "pull" , "origin", "master"])

            if build == build_opm:
                cmake_options = opm_cmake_options
            elif build == build_ert:
                cmake_options = ert_cmake_options

            build(cmake, cmake_options)


    cleanup()






if __name__ == "__main__":
    multi_pr( sys.argv[1:] )
