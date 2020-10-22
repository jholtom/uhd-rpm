Name:           uhd
Version:	    4.0.0.0
Release:        1%{?dist}
Summary:        Universal Hardware Driver for Ettus Research products
License:        GPLv3+
Group:          Applications/Engineering
Url:            https://github.com/EttusResearch/uhd
%undefine _disable_source_fetch
Source:         https://github.com/EttusResearch/uhd/archive/v4.0.0.0.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  boost-devel, libusb1-devel, python3-cheetah, ncurses-devel
BuildRequires:  python3-docutils, doxygen, pkgconfig, libpcap-devel
BuildRequires:  python3-numpy, vim-common
BuildRequires:  python3-mako, python3-requests, python3-devel, tar, python3-ruamel-yaml

Requires(pre):  shadow-utils, glibc-common
Requires:       python3-tkinter

%description
The UHD is the universal hardware driver for Ettus Research products.
The goal of the UHD is to provide a host driver and API for current and
future Ettus Research products. It can be used standalone without GNU Radio.

%package devel
Summary:        Development files for UHD
Requires:       %{name} = %{version}-%{release}
Requires: boost-devel
%description devel
Development files for the Universal Hardware Driver (UHD).

%package doc
Summary:        Documentation files for UHD
BuildArch:      noarch
%description doc
Documentation for the Universal Hardware Driver (UHD).

%package examples
Summary:        Example files for UHD
Requires:       %{name} = %{version}-%{release}
%description examples
Examples for the Universal Hardware Driver (UHD).

%package tools
Summary:        Tools for working with / debugging USRP device
Requires:       %{name} = %{version}-%{release}
%description tools
Tools that are useful for working with and/or debugging USRP device.

%package python3
Summary:        Python3 UHD Library
Requires:       %{name} = %{version}-%{release}
%description python3
Python3 UHD Library

%prep
%setup -n %{name}-%{version}

%build
mkdir -p host/build
pushd host/build
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON -DCMAKE_INSTALL_PREFIX:PATH=%{_prefix} -DENABLE_PYTHON_API=ON ..
make %{?_smp_mflags}
popd

# tools
pushd tools/uhd_dump
make %{?_smp_mflags}
popd

%check
#cd host/build
#make test

%install
pushd host/build
make install DESTDIR=%{buildroot}

# USB permissions
mkdir -p %{buildroot}%{_sysconfdir}/udev/rules.d
mv %{buildroot}%{_libdir}/uhd/utils/uhd-usrp.rules %{buildroot}%{_sysconfdir}/udev/rules.d/

# Set recommended limits
mkdir -p %{buildroot}%{_prefix}/lib/sysctl.d
echo -e 'net.core.wmem_max=33554432\nnet.core.rmem_max=33554432' > %{buildroot}%{_prefix}/lib/sysctl.d/90-override.conf

# Set thread prioirty
mkdir -p %{buildroot}%{_sysconfdir}/security/limits.d
echo -e '@wheel    - rtprio    99' > %{buildroot}%{_sysconfdir}/security/limits.d/90-uhd-usrp.conf

# Remove tests
rm -rf %{buildroot}%{_libdir}/uhd/tests

# Move the utils stuff to libexec dir
mkdir -p %{buildroot}%{_libexecdir}/uhd
mv %{buildroot}%{_libdir}/uhd/utils/* %{buildroot}%{_libexecdir}/uhd

popd

# Package base docs to base package
mkdir _tmpdoc
mv %{buildroot}%{_docdir}/%{name}/{LICENSE,README.md} _tmpdoc

# tools
install -Dpm 0755 tools/usrp_x3xx_fpga_jtag_programmer.sh %{buildroot}%{_bindir}/usrp_x3xx_fpga_jtag_programmer.sh
install -Dpm 0755 tools/uhd_dump/chdr_log %{buildroot}%{_bindir}/chdr_log

%clean
rm -rf $RPM_BUILD_ROOT

%post
/usr/bin/udevadm control --reload-rules
/usr/bin/udevadm trigger
/usr/sbin/sysctl -w net.core.wmem_max=33554432
/usr/sbin/sysctl -w net.core.rmem_max=33554432
/sbin/ldconfig

%postun
/usr/bin/udevadm control --reload-rules
/sbin/ldconfig

%files
%doc _tmpdoc/*
%{_bindir}/uhd_*
%{_bindir}/usrp2*
%{_sysconfdir}/udev/rules.d/uhd-usrp.rules
%{_prefix}/lib/sysctl.d/90-override.conf
%{_sysconfdir}/security/limits.d/90-uhd-usrp.conf
%{_libdir}/lib*.so.*
%{_libexecdir}/uhd
%{_mandir}/man1/*.1*
%{_datadir}/uhd

%files devel
%{_includedir}/*
%{_libdir}/lib*.so
%{_libdir}/cmake/uhd/*.cmake
%{_libdir}/pkgconfig/*.pc

%files examples
%{_libdir}/uhd/examples/*

%files doc
%doc %{_docdir}/%{name}/doxygen

%files tools
%doc tools/README.md
%{_bindir}/usrp_x3xx_fpga_jtag_programmer.sh
%{_bindir}/rfnoc_image_builder
%{_bindir}/chdr_log

%files python3
%{_libdir}/python3.6/site-packages/uhd/*

%changelog

