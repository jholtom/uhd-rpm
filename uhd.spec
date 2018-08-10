Name:           uhd
Version:	%{VERSION}
Release:        1%{?dist}
Summary:        Universal Hardware Driver for Ettus Research products
License:        GPLv3+
Group:          Applications/Engineering
Url:            https://github.com/EttusResearch/uhd
Source:         %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  gcc gcc-c++ cmake
BuildRequires:  boost-devel, libusb1-devel
BuildRequires:  docutils, doxygen, pkgconfig, libpcap-devel
BuildRequires:  python-mako

%description
The UHD is the universal hardware driver for Ettus Research products.
The goal of the UHD is to provide a host driver and API for current and
future Ettus Research products. It can be used standalone without GNU Radio.

%package devel
Summary:        Development files for UHD
Requires:       %{name} = %{version}-%{release}
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

%prep
%setup -n %{name}-%{version}

%build
mkdir -p host/build
pushd host/build
%cmake ../
make %{?_smp_mflags}
popd

# tools
pushd tools/uhd_dump
make %{?_smp_mflags} CFLAGS="%{optflags}" LDFLAGS="%{?__global_ldflags}"
popd

%check
cd host/build 
make test

%install
pushd host/build
make install DESTDIR=%{buildroot}

# Fix udev rules and use dynamic ACL management for device
sed -i 's/BUS==/SUBSYSTEM==/;s/SYSFS{/ATTRS{/;s/MODE:="0666"/MODE:="0660", ENV{ID_SOFTWARE_RADIO}="1"/' %{buildroot}%{_libdir}/uhd/utils/uhd-usrp.rules
mkdir -p %{buildroot}%{_prefix}/lib/udev/rules.d
mv %{buildroot}%{_libdir}/uhd/utils/uhd-usrp.rules %{buildroot}%{_prefix}/lib/udev/rules.d/10-usrp-uhd.rules

# Set recommended limits
mkdir -p %{buildroot}%{_prefix}/lib/sysctl.d
echo -e 'net.core.wmem_max=576000\nnet.core.rmem_max=33554432' > %{buildroot}%{_prefix}/lib/sysctl.d/90-override.conf

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
/usr/sbin/sysctl -w net.core.wmem_max=576000
/usr/sbin/sysctl -w net.core.rmem_max=33554432
/sbin/ldconfig

%postun
/sbin/ldconfig

%pre
getent group usrp >/dev/null || groupadd -r usrp >/dev/null

%files
%exclude %{_datadir}/uhd/images
%doc _tmpdoc/*
%{_bindir}/uhd_*
%{_bindir}/usrp2*
%{_prefix}/lib/udev/rules.d/10-usrp-uhd.rules
%{_prefix}/lib/sysctl.d/90-override.conf
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
%{_bindir}/chdr_log

%changelog

