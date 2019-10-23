%{?scl:%scl_package oprofile}

Summary: System wide profiler
Name: %{?scl_prefix}oprofile
Version: 1.3.0
Release: 3%{?dist}
License: GPLv2+ and LGPLv2+
Group: Development/System
#
Source0: http://downloads.sourceforge.net/oprofile/oprofile-%{version}.tar.gz
#FIXME a workaround until java-1.6.0-openjdk-devel is available on all archs
Source1: openjdk-include.tar.gz
Patch1: oprofile-ppc_null_event.patch
Patch2: oprofile-no_orphan.patch
Requires: binutils
Requires: which
Requires(pre): shadow-utils
Requires(postun): shadow-utils
%{?scl:Requires:%scl_runtime}

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
%ifnarch s390x s390
BuildRequires: papi-devel
%endif
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
%setup -q -n oprofile-%{version} -a1
%patch1 -p1 -b .ppc_null_event
%patch2 -p1 -b .noorphan

./autogen.sh

%build

%configure \
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

%if 0%{?scl:1}
# if developer tools set need to put the agentlib in an appropriate place
mv %{buildroot}%{_libdir}/oprofile/* %{buildroot}%{_libdir}
rmdir %{buildroot}%{_libdir}/oprofile
%else
mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d
echo "%{_libdir}/oprofile" > %{buildroot}%{_sysconfdir}/ld.so.conf.d/oprofile-%{_arch}.conf
%endif


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

%post jit -p /sbin/ldconfig

%postun jit -p /sbin/ldconfig

%files jit
%defattr(-,root,root)

%if 0%{?scl:1}
%{_libdir}/*
%else
%{_libdir}/oprofile
%{_sysconfdir}/ld.so.conf.d/*
%endif

%changelog
* Thu Jul 25 2019 William Cohen <wcohen@redhat.com> - 1.3.0-3
- Correctly kill child process when error occurs during setup.

* Fri Aug 3 2018 William Cohen <wcohen@redhat.com> - 1.3.0-2
- Fix handling of null event name on ppc. rhbz1609797

* Mon Jul 16 2018 William Cohen <wcohen@redhat.com> - 1.3.0-1
- Rebase to oprofile-1.3.0.

* Wed Apr 25 2018 William Cohen <wcohen@redhat.com> - 1.2.0-2.1
- Power9 cpu recognition.

* Thu Feb 22 2018 William Cohen <wcohen@redhat.com> - 1.2.0-2
- Rebuilt.

* Wed Jul 26 2017 William Cohen <wcohen@redhat.com> - 1.2.0-1
- Rebase to oprofile-1.2.0.

* Fri Jun 16 2017 Will Cohen <wcohen@redhat.com> - 1.2.0-0.20170616git647ca9d0
- Rebuild on oprofile git snapshot.

* Wed Oct 12 2016 Will Cohen <wcohen@redhat.com> - 1.1.0-4
- Update events non-x86 architectures (aarch64, power, zseries)
- Add support for newer Intel processors.

* Thu Sep 15 2016 Will Cohen <wcohen@redhat.com> - 1.1.0-3
- Avoid duplicate event names for Nehalem and Westmere processors.

* Thu Aug 13 2015 Will Cohen <wcohen@redhat.com> - 1.1.0-2
- Locate jvm agent libjvmti in a LD_LIBRARY_PATH directory.

* Tue Jul 21 2015 Will Cohen <wcohen@redhat.com> - 1.1.0-1
- Rebase to oprofile-1.1.0.

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
