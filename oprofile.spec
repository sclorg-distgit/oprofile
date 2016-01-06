%{?scl:%scl_package oprofile}

Summary: System wide profiler
Name: %{?scl_prefix}oprofile
Version: 0.9.9
Release: 7%{?dist}
License: GPLv2+ and LGPLv2+
Group: Development/System
#
Source0: http://downloads.sourceforge.net/oprofile/oprofile-%{version}.tar.gz
#FIXME a workaround until java-1.6.0-openjdk-devel is available on all archs
Source1: openjdk-include.tar.gz
Requires: binutils
Requires: which
Requires(pre): shadow-utils
Requires(postun): shadow-utils
%{?scl:Requires:%scl_runtime}
Patch10: oprofile-0.4-guess2.patch
Patch83: oprofile-0.9.7-xen.patch
Patch303: oprofile-num_symbolic.patch
Patch304: oprofile-xml.patch
Patch305: oprofile-rhbz1121205.patch
Patch400: oprofile-haswell.patch
Patch401: oprofile-silvermont.patch
Patch402: oprofile-broadwell.patch
Patch500: oprofile-aarch64.patch
Patch600: oprofile-power8.patch
Patch601: oprofile-ppc64le.patch
Patch700: oprofile-hugepage.patch
Patch800: oprofile-defaultmask.patch
Patch801: oprofile-extramask.patch
Patch802: oprofile-maskarray.patch
Patch803: oprofile-env.patch

URL: http://oprofile.sf.net

#If oprofile doesn't build on an arch, report it and will add ExcludeArch tag.
BuildRequires: qt-devel
BuildRequires: libxslt
BuildRequires: docbook-style-xsl
BuildRequires: docbook-utils
BuildRequires: elinks
BuildRequires: gtk2-devel
BuildRequires: automake
BuildRequires: libtool
%if 0%{?rhel} >= 7 || 0%{?fedora} >= 15
BuildRequires: binutils-static
BuildRequires: libpfm-devel >= 4.3.0
%else
BuildRequires: %{?scl_prefix}binutils-devel
BuildRequires: binutils-devel
%endif
%if 0%{?rhel} == 6
BuildRequires: papi-devel
%endif
%if 0%{?rhel} >= 6
BuildRequires: popt-devel
%else
BuildRequires: popt
%endif

#BuildRequires: java-devel
#BuildRequires: jpackage-utils
#BuildRequires: java-1.6.0-openjdk-devel

BuildRoot: %{_tmppath}/%{name}-root

%description
OProfile is a profiling system for systems running Linux. The
profiling runs transparently during the background, and profile data
can be collected at any time. OProfile makes use of the hardware performance
counters provided on Intel P6, and AMD Athlon family processors, and can use
the RTC for profiling on other x86 processor types.

See the HTML documentation for further details.

%package devel
Summary: Header files and libraries for developing apps which will use oprofile
Group: Development/Libraries
Requires: %{?scl_prefix}oprofile = %{version}-%{release}
Provides: %{?scl_prefix}oprofile-static = %{version}-%{release}

%description devel

Header files and libraries for developing apps which will use oprofile.

%package gui
Summary: GUI for oprofile
Group: Development/System
Requires: %{?scl_prefix}oprofile = %{version}-%{release}

%description gui

The oprof_start GUI for oprofile.

%package jit
Summary: Libraries required for profiling Java and other JITed code
Group: Development/System
Requires: %{?scl_prefix}oprofile = %{version}-%{release}
#Requires: java >= 1.6
#Requires: jpackage-utils
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig
Requires: /etc/ld.so.conf.d

%description jit
This package includes a base JIT support library, as well as a Java
agent library.

%prep
%setup -q -n %{pkg_name}-%{version} -a1
%patch10 -p1 -b .guess2
%patch83 -p1 -b .xen
%patch303 -p1 -b .num_symbolic
%patch304 -p1 -b .xml
%patch305 -p1 -b .xml
%patch400 -p1 -b .haswell
%patch401 -p1 -b .silvermont
%patch402 -p1 -b .broadwell
%patch500 -p1 -b .aarch64
%patch600 -p1 -b .power8
%patch601 -p1 -b .ppc64le
%patch700 -p1
%patch800 -p1
%patch801 -p1
%patch802 -p1
%patch803 -p1

./autogen.sh

%build

%global qt_ver qt4

#The CXXFLAGS below is temporary to work around
# bugzilla #113909
CXXFLAGS=-g;     export CXXFLAGS

%configure \
--enable-gui=%{qt_ver} \
--with-java=`pwd`/java-1.6.0-openjdk-1.6.0.0

make CFLAGS="$RPM_OPT_FLAGS"

#tweak the manual pages
find -path "*/doc/*.1" -exec \
    sed -i -e \
     's,/doc/oprofile/,/doc/oprofile-%{version}/,g' {} \;

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_mandir}/man1

make DESTDIR=%{buildroot} INSTALL="install -p" install

# We want the manuals in the special doc dir, not the generic doc install dir.
# We build it in place and then move it away so it doesn't get installed
# twice. rpm can specify itself where the (versioned) docs go with the
# %%doc directive.
mkdir docs.installed
mv %{buildroot}%{_datadir}/doc/oprofile/* docs.installed/

mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d
echo "%{_libdir}/oprofile" > %{buildroot}%{_sysconfdir}/ld.so.conf.d/oprofile-%{_arch}.conf

%pre
getent group oprofile >/dev/null || groupadd -r -g 16 oprofile
getent passwd oprofile >/dev/null || \
useradd -g oprofile -d /var/lib/oprofile -M -r -u 16 -s /sbin/nologin \
    -c "Special user account to be used by OProfile" oprofile
exit 0

%postun
# do not try to remove existing oprofile user or group

%files
%defattr(-,root,root)
%doc  docs.installed/*
%doc COPYING

%{_bindir}/*

%{_mandir}/man1/*

%{_datadir}/oprofile

%files devel
%defattr(-,root,root)

%{_includedir}/opagent.h

%files gui
%defattr(-,root,root)

%{_bindir}/oprof_start

%post jit -p /sbin/ldconfig

%postun jit -p /sbin/ldconfig

%files jit
%defattr(-,root,root)

%{_libdir}/oprofile
%{_sysconfdir}/ld.so.conf.d/*

%changelog
* Thu Apr 23 2015 Will Cohen <wcohen@redhat.com> - 0.9.9-7
- LLC_REFS and LLC_MISSES do not work on some CPUs.
- incorrect handling of default unit masks longer than 11 characters
- Oprofile updates for Avoton
- Unable to profile jited JVM code when using static huge pages
- operf causes rpmbuild to fail

* Wed Sep 17 2014 Will Cohen <wcohen@redhat.com> - 0.9.9-6
- Update support for Intel Silvermont (Avoton).
- Enable configure for ppc64le.

* Mon Aug 18 2014 Will Cohen <wcohen@redhat.com> - 0.9.9-5
- Update Intel Haswell events.
- Add support for Intel Silvermont (Avoton).
- Add support for Intel Broadwell.
- Add support for aarch64.
- Update IBM power8 events.

* Wed May 28 2014 Will Cohen <wcohen@redhat.com> - 0.9.9-2.1
- Correct xml output.

* Fri May 16 2014 Will Cohen <wcohen@redhat.com> - 0.9.9-1.1
- Rebase on oprofile-0.9.9.
