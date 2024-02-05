#define api_version	3
%define major	4

%define libname	%mklibname %{name}
%define devname	%mklibname %{name} -d

%define oldlibname_orig	%mklibname %{name} 3
%define oldlibname		%mklibname %{name} 3 3
%define olddevname		%mklibname -d %{name} 3
%define oldstaticdevname	%mklibname -d -s %{name} 3

%bcond_with	ispc

# limit the maximum number of parallel building processes to avoid
# running out of memory during building
%global		_smp_ncpus_max 2

Name:		embree
Version:	4.3.0
Release:	1
Summary:	A collection of high-performance ray tracing kernels
Group:		Graphics/3D
License:	ASL 2.0
URL:		https://embree.github.io
Source:		https://github.com/%{name}/%{name}/archive/v%{version}/%{name}-%{version}.tar.gz
BuildRequires:	cmake ninja
%if %{with ispc} 
BuildRequires:	ispc
%endif
BuildRequires:	pkgconfig(glut)
BuildRequires:	pkgconfig(glfw3)
BuildRequires:	pkgconfig(xmu)
BuildRequires:	pkgconfig(libjpeg)
BuildRequires:	pkgconfig(libpng)
BuildRequires:	pkgconfig(OpenImageIO)
BuildRequires:	pkgconfig(tbb)

#BuildRequires:	pkgconfig(freeglut)
#BuildRequires:	pkgconfig(OpenEXR)

%description
A collection of high-performance ray tracing kernels intended to
graphics application engineers that want to improve the performance of
their photo-realistic rendering applications.

#----------------------------------------------------------------------

%package -n %{libname}
Summary:	A collection of high-performance ray tracing kernels
Group:		System/Libraries
#Requires:	%{_lib}tbb2 >= 4.0
#Provides:	%{libname_orig} = %{version}-%{release}
#Provides:	%{name}%{api_version} = %{version}-%{release}
Obsoletes:	%{oldlibname}
Obsoletes:	%{oldlibname_orig}
Obsoletes:	%{name}3 < %{version}-%{release}

%description -n %{libname}
A collection of high-performance ray tracing kernels intended to
graphics application engineers that want to improve the performance of
their photo-realistic rendering applications.

This package contains the library needed to run programs dynamically
linked with embree.

%files -n %{libname}
%{_libdir}/lib%{name}%{major}{,.*}

#----------------------------------------------------------------------

%package -n %{devname}
Summary:	Headers and development files of the embree library
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
#Provides:	%{name}%{api_version}-devel = %{version}-%{release}
#Provides:	%{libname_orig}-devel = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}
Obsoletes:	%{olddevname}
Obsoletes:	%{oldlibname_orig}-devel

%description -n %{devname}
Development files for the embree library. Install this package if you
want to compile applications using the embree library.

%files -n %{devname}
%license LICENSE.txt
%doc README.md CHANGELOG.md readme.pdf
%doc third-party-programs{,-TBB,-DPCPP,-OIDN,-oneAPI-DPCPP}.txt
%{_libdir}/lib%{name}%{major}.so
%{_includedir}/%{name}%{major}/
%{_libdir}/cmake/%{name}-%{version}/
%{_mandir}/man3/*

#----------------------------------------------------------------------

%prep
%autosetup -n %{name}-%{version}

%build
#	-DEMBREE_MAX_ISA:STRING="AVX512SKX" \
%cmake \
	-DEMBREE_IGNORE_CMAKE_CXX_FLAGS:BOOL=OFF \
	-DCMAKE_CXX_FLAGS_RELEASE:STRING="%{optflags} -Wl,--as-needed" \
	-DCMAKE_C_FLAGS_RELEASE:STRING="%{optflags} -Wl,--as-needed" \
	-DEMBREE_COMPACT_POLYS:BOOL=ON \
	-DEMBREE_RAY_MASK:BOOL=ON \
	-DEMBREE_BACKFACE_CULLING:BOOL=OFF \
	-DEMBREE_FILTER_FUNCTION:BOOL=ON \
	-DEMBREE_ISPC_SUPPORT:BOOL=%{?with_ispc:ON}%{!?with_ispc:OFF} \
	-DEMBREE_MAX_ISA=NONE \
%ifarch x86_64
	-DEMBREE_ISA_SSE2:BOOL=ON \
	-DEMBREE_ISA_SSE4:BOOL=ON \
	-DEMBREE_ISA_AVX:BOOL=ON \
	-DEMBREE_ISA_AVX2:BOOL=ON \
%else
	-DEMBREE_ARM:BOOL=ON \
	-DEMBREE_ISA_NEON:BOOL=ON \
%endif
	-DEMBREE_STATIC_LIB:BOOL=OFF \
	-DEMBREE_TUTORIALS:BOOL=ON \
	-DEMBREE_TESTING:BOOL=ON \
	-G Ninja
%ninja_build

%install
%ninja_install -C build

# Remove installers
rm -f %{buildroot}%{_prefix}/%{name}-vars.{csh,sh}

# Relocate doc files
mv %{buildroot}%{_docdir}/%{name}4 %{buildroot}%{_docdir}/%{name}

# install docs by hand
rm -f %{buildroot}%{_docdir}/%{name}/LICENSE.txt
rm -f %{buildroot}%{_docdir}/%{name}/README.md
rm -f %{buildroot}%{_docdir}/%{name}/readme.pdf
rm -f %{buildroot}%{_docdir}/%{name}/CHANGELOG.md
rm -f %{buildroot}%{_docdir}/%{name}/third-party-programs{,-TBB,-DPCPP,-OIDN,-oneAPI-DPCPP}.txt

# Remove the testing products
rm -fr %{buildroot}%{_prefix}/src
rm -fr %{buildroot}%{_bindir}/models
rm -f  %{buildroot}%{_bindir}/embree_*

%check
pushd build
ctest || :
popd

