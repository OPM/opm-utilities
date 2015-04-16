#!/usr/bin/env bash

set +e
script_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
source $script_dir/set_environment.sh

#Function which clones or updates from a GIT repository
function clone_or_update() {
	local git_url=$1
	local src_dir=$2
	if [ -d $src_dir ]; then
		cd $src_dir
		git pull origin master
	else
		git clone --recursive $git_url $src_dir
	fi
}

patchname=`mktemp`
cat << EOF > $patchname
--- util_lockf_orig.c	2015-04-09 16:01:49.348284973 +0200
+++ util_lockf.c	2015-04-09 16:01:27.228175286 +0200
@@ -70,7 +70,7 @@
   if (strcmp(mode , "w") == 0)
     flags += O_CREAT;
   
-  fd = open(filename , flags);
+  fd = open(filename , flags, S_IRUSR|S_IWUSR);
   if (fd == -1) 
     util_abort("%s: failed to open:%s with flags:%d \n",__func__ , filename , flags);
   
EOF

# Clone ERT
clone_or_update "https://github.com/OPM/ResInsight.git" "$opm_git_dir/ResInsight"

# Patch it
patch "$opm_git_dir/ResInsight/ThirdParty/Ert/devel/libert_util/src/util_lockf.c" < $patchname

#Build
mkdir -p "$opm_git_dir/ResInsight-build"
cd "$opm_git_dir/ResInsight-build"
cmake "$opm_git_dir/ResInsight"
make
