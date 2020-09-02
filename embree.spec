%define pkgname		embree
%define api_version	3
%define libmajor	3
%define libname_orig	%mklibname %{pkgname} %{api_version}
%define libname		%mklibname %{pkgname} %{api_version} %{libmajor}
%define develname	%mklibname -d %{pkgname} %{api_version}
%define staticdevname	%mklibname -d -s %{pkgname} %{api_version}

# limit the maximum number of parallel building processes to avoid
# running out of memory during building
%global		_smp_ncpus_max 2

Name:		%{pkgname}%{api_version}
Version:	3.11.0
Release:	1
Summary:	A collection of high-performance ray tracing kernels
Group:		Graphics/3D
License:	ASL 2.0
URL:		https://embree.github.io
Source:		https://github.com/%{pkgname}/%{pkgname}/archive/v%{version}/%{pkgname}-%{version}.tar.gz
BuildRequires:	cmake
BuildRequires:	gcc-c++
BuildRequires:	ispc
BuildRequires:	pkgconfig(freeglut)
BuildRequires:	pkgconfig(glfw3)
BuildRequires:	pkgconfig(OpenEXR)
BuildRequires:	pkgconfig(tbb)
BuildRequires:	pkgconfig(xmu)
# Use 64bit architectures because of SSE2 and up
ExclusiveArch:	x86_64

%description
A collection of high-performance ray tracing kernels intended to
graphics application engineers that want to improve the performance of
their photo-realistic rendering applications.

%package -n %{libname}
Summary:	A collection of high-performance ray tracing kernels
Group:		System/Libraries
Requires:	%{_lib}tbb2 >= 4.0
Provides:	%{libname_orig} = %{version}-%{release}
Provides:	%{pkgname}%{api_version} = %{version}-%{release}

%description -n %{libname}
A collection of high-performance ray tracing kernels intended to
graphics application engineers that want to improve the performance of
their photo-realistic rendering applications.

This package contains the library needed to run programs dynamically
linked with embree.

%package -n %{develname}
Summary:	Headers and development files of the embree library
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	%{pkgname}%{api_version}-devel = %{version}-%{release}
Provides:	%{libname_orig}-devel = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	%{pkgname}-devel = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}

%description -n %{develname}
Development files for the embree library. Install this package if you
want to compile applications using the embree library.

%prep
%autosetup -n %{pkgname}-%{version}

%build
%cmake \
	-DEMBREE_IGNORE_CMAKE_CXX_FLAGS:BOOL=OFF \
	-DCMAKE_CXX_FLAGS_RELEASE:STRING="%{optflags}" \
	-DCMAKE_C_FLAGS_RELEASE:STRING="%{optflags}" \
	-DEMBREE_RAY_MASK:BOOL=ON \
	-DEMBREE_BACKFACE_CULLING:BOOL=OFF \
	-DEMBREE_FILTER_FUNCTION:BOOL=ON \
	-DEMBREE_MAX_ISA:STRING="AVX512SKX" \
	-DEMBREE_TUTORIALS:BOOL=OFF

%make_build
cd ..

%install
%make_install -C build

# Remove installed doc files
rm -rf %{buildroot}%{_docdir}/%{name}

%files -n %{libname}
%{_libdir}/*.so.%{libmajor}{,.*}

%files -n %{develname}
%license LICENSE.txt
%doc README.md CHANGELOG.md readme.pdf
%{_libdir}/lib*.so
%{_includedir}/*
%{_libdir}/cmake/%{pkgname}-%{version}
%{_mandir}/man3/*
