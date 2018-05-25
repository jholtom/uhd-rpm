Name:           uhd
Version:	%{VERSION}
Release:        1%{?dist}
Summary:        Ettus Research - USRP Hardware Driver
License:        GPLv3
Group:          Development/Libraries/C and C++
Url:            https://github.com/EttusResearch/uhd
Source:         %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  boost-devel
BuildRequires:  libusb1-devel
BuildRequires:	python-mako
BuildRequires:	doxygen
BuildRequires:	python-docutils
BuildRequires:	cmake
BuildRequires:	make
BuildRequires:	gcc
BuildRequires:	gcc-c++

%description
Ettus Research - USRP Hardware Driver

%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries/C and C++
Requires:	%{name} = %{version}

%description    devel
Ettus Research - USRP Hardware Driver

%prep
%setup -n %{name}-%{version}

%build
cd host
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr -DLIB_SUFFIX=64
make %{?_smp_mflags}

%check
cd host/build 
make test

%install
rm -rf $RPM_BUILD_ROOT
cd host/build
make install DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%post
ldconfig

%postun
ldconfig

%files
%defattr(-,root,root,-)
%{_libdir}/libuhd.so.*
%{_mandir}/man1/*
%{_docdir}/uhd/*

%files devel
%defattr(-,root,root)
%{_bindir}/*
%{_includedir}/uhd/
%{_includedir}/uhd.h
%{_libdir}/libuhd.so
%{_libdir}/uhd/
%{_libdir}/pkgconfig/uhd.pc
%{_libdir}/cmake/uhd/
%{_datadir}/uhd/rfnoc/

%changelog

