#!/bin/bash

# This scripts prepares the pbuilder basetgz for xenial
# Needs to be run as root

# Write convenience pbuilder-rc to root dir
if ! test -f /root/.pbuilderrc
then
  echo '
  # Codenames for Debian suites according to their alias. Update these when
  # needed.
  UNSTABLE_CODENAME="sid"
  TESTING_CODENAME="buster"
  STABLE_CODENAME="stretch"
  STABLE_BACKPORTS_SUITE="$STABLE_CODENAME-backports"

  # List of Debian suites.
  DEBIAN_SUITES=($UNSTABLE_CODENAME $TESTING_CODENAME $STABLE_CODENAME $STABLE_BACKPORTS_SUITE
      "experimental" "unstable" "testing" "stable")

  # List of Ubuntu suites. Update these when needed.
  UBUNTU_SUITES=("xenial" "wily" "vivid" "utopic" "trusty")

  # Mirrors to use. Update these to your preferred mirror.
  DEBIAN_MIRROR="deb.debian.org"
  UBUNTU_MIRROR="mirrors.kernel.org"

  # Optionally use the changelog of a package to determine the suite to use if
  # none set.
  if [ -z "${DIST}" ] && [ -r "debian/changelog" ]; then
      DIST=$(dpkg-parsechangelog --show-field=Distribution)
  fi

  # Optionally set a default distribution if none is used. Note that you can set
  # your own default (i.e. ${DIST:="unstable"}).
  : ${DIST:="$(lsb_release --short --codename)"}

  # Optionally change Debian codenames in $DIST to their aliases.
  case "$DIST" in
      $UNSTABLE_CODENAME)
          DIST="unstable"
          ;;
      $TESTING_CODENAME)
          DIST="testing"
          ;;
      $STABLE_CODENAME)
          DIST="stable"
          ;;
  esac

  # Optionally set the architecture to the host architecture if none set. Note
  # that you can set your own default (i.e. ${ARCH:="i386"}).
  : ${ARCH:="$(dpkg --print-architecture)"}

  NAME="$DIST"
  if [ -n "${ARCH}" ]; then
      NAME="$NAME-$ARCH"
      DEBOOTSTRAPOPTS=("--arch" "$ARCH" "${DEBOOTSTRAPOPTS[@]}")
  fi
  BASETGZ="/var/cache/pbuilder/$NAME-base.tgz"
  DISTRIBUTION="$DIST"
  BUILDRESULT="/var/cache/pbuilder/$NAME/result/"
  APTCACHE="/var/cache/pbuilder/$NAME/aptcache/"
  BUILDPLACE="/var/cache/pbuilder/build/"

  if $(echo ${DEBIAN_SUITES[@]} | grep -q $DIST); then
      # Debian configuration
      MIRRORSITE="http://$DEBIAN_MIRROR/debian/"
      COMPONENTS="main contrib non-free"
      if $(echo "$STABLE_CODENAME stable" | grep -q $DIST); then
          OTHERMIRROR="$OTHERMIRROR | deb $MIRRORSITE $STABLE_BACKPORTS_SUITE $COMPONENTS"
      fi
  elif $(echo ${UBUNTU_SUITES[@]} | grep -q $DIST); then
      # Ubuntu configuration
      MIRRORSITE="http://$UBUNTU_MIRROR/ubuntu/"
      COMPONENTS="main restricted universe multiverse"
  else
      echo "Unknown distribution: $DIST"
      exit 1
  fi
  ' > /root/.pbuilderrc
fi

# Create link so debootstrap recognizes xenial distro
ln -sf /usr/share/debootstrap/scripts/gutsy /usr/share/debootstrap/scripts/xenial

# Import ubuntu key
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32

# Inject some stuff used everywhere to save some time
GENERIC_EXTRA_PACKAGES="texlive-latex-extra doxygen cmake g++ build-essential libboost-dev apt-utils"

# Finally create the base tgz
DIST=xenial pbuilder --create --debootstrapopts "--keyring=/etc/apt/trusted.gpg" --extrapackages "$GENERIC_EXTRA_PACKAGES"
