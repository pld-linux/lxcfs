Summary:	FUSE filesystem for LXC
Name:		lxcfs
Version:	2.0.2
Release:	0.1
License:	Apache v2.0
Group:		Applications/System
Source0:	https://linuxcontainers.org/downloads/lxcfs/%{name}-%{version}.tar.gz
# Source0-md5:	fea9124c9d6d7370e12c4a3f0d405541
URL:		https://linuxcontainers.org/lxcfs/
Patch0:		0001-skip-empty-entries-under-proc-self-cgroup.patch
Patch1:		pld.patch
BuildRequires:	help2man
BuildRequires:	libfuse-devel
BuildRequires:	pam-devel
BuildRequires:	pkg-config
BuildRequires:	pld-release
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_libexecdir	%{_prefix}/lib

%description
LXCFS is a simple userspace filesystem designed to work around some
current limitations of the Linux kernel.

Specifically, it's providing two main things:
- A set of files which can be bind-mounted over their /proc originals
  to provide CGroup-aware values.
- A cgroupfs-like tree which is container aware.

The code is pretty simple, written in C using libfuse and glib.

The main driver for this work was the need to run systemd based
containers as a regular unprivileged user while still allowing systemd
inside the container to interact with cgroups.

Now with the introduction of the cgroup namespace in the Linux kernel,
that part is no longer necessary on recent kernels and focus is now on
making containers feel more like a real independent system through the
proc masking feature.

%package -n pam-pam_cgfs
Summary:	CGroup FS pam module
Group:		Libraries

%description -n pam-pam_cgfs
When a user logs in, this pam module will create cgroups which the
user may administer, either for all controllers or for any controllers
listed on the command line.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
%configure \
	--with-distro=pld

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{%{systemdunitdir},%{_libexecdir},%{_includedir}/%{name},%{_localstatedir}/lib/%{name}}

# The shared library liblxcfs.so used by lxcfs is not supposed to be used by
# any other program. So we follow best practice and install it in
# %{_prefix}/lib/lxcfs. Note that lxcfs *expects* liblxcfs.so to be found in
# %{_prefix}/lib/lxcfs when it cannot find it in the lib.so path.
install -p .libs/liblxcfs.so $RPM_BUILD_ROOT%{_libexecdir}
rm $RPM_BUILD_ROOT%{_libdir}/liblxcfs.so*
rm $RPM_BUILD_ROOT%{_libdir}/liblxcfs.la

%clean
rm -rf $RPM_BUILD_ROOT

%if 0
%pre
%service_add_pre lxcfs.service

%post
%service_add_post lxcfs.service

%preun
%service_del_preun lxcfs.service

%postun
%service_del_postun lxcfs.service
%endif

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog README
%attr(755,root,root) %{_bindir}/lxcfs
%{_mandir}/man1/lxcfs.1*
%{systemdunitdir}/lxcfs.service
%attr(754,root,root) /etc/rc.d/init.d/lxcfs
%dir %{_datadir}/%{name}
%attr(755,root,root) %{_datadir}/%{name}/lxc.mount.hook
%attr(755,root,root) %{_datadir}/%{name}/lxc.reboot.hook
%dir %{_localstatedir}/lib/%{name}

%{_datadir}/lxc/config/common.conf.d/00-lxcfs.conf

# The lxcfs executable requires liblxcfs.so be installed. It calls dlopen() to
# dynamically reload the shared library on upgrade. This is important. Do *not*
# split into a separate package and do not turn this into a versioned shared
# library! (This shared library allows lxcfs to be updated without having to
# restart it which is good when you have important system containers running!)
%{_libexecdir}/liblxcfs.so

%files -n pam-pam_cgfs
%defattr(644,root,root,755)
/%{_lib}/security/pam_cgfs.so
