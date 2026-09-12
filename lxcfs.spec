Summary:	FUSE filesystem for LXC
Name:		lxcfs
Version:	7.0.0
Release:	1
License:	Apache v2.0
Group:		Applications/System
Source0:	https://linuxcontainers.org/downloads/lxcfs/%{name}-%{version}.tar.gz
# Source0-md5:	30987accb7feffe4847354133547cf27
Source1:	lxcfs.init
Patch0:		%{name}-no-gold.patch
URL:		https://linuxcontainers.org/lxcfs/
BuildRequires:	help2man
BuildRequires:	libfuse3-devel
BuildRequires:	meson >= 0.50
BuildRequires:	ninja >= 1.5
BuildRequires:	pkg-config
BuildRequires:	python3-jinja2
BuildRequires:	rpmbuild(macros) >= 2.042
BuildRequires:	systemd-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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

%prep
%setup -q
%patch -P0 -p1

%build
%meson \
	-Dinit-script=systemd

%meson_build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{,%{systemdunitdir},/etc/rc.d/init.d,/var/lib/%{name}}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

%meson_install

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog README
%attr(755,root,root) %{_bindir}/lxcfs
%{_mandir}/man1/lxcfs.1*
%{systemdunitdir}/lxcfs.service
%attr(754,root,root) /etc/rc.d/init.d/lxcfs
%dir %{_datadir}/%{name}
%dir %{_libdir}/%{name}
%attr(755,root,root) %{_datadir}/%{name}/lxc.mount.hook
%attr(755,root,root) %{_datadir}/%{name}/lxc.reboot.hook
%dir %{_localstatedir}/lib/%{name}
# lxc (if installed) picks the hook config up from here; lxcfs itself does not need lxc
%dir %{_datadir}/lxc
%dir %{_datadir}/lxc/config
%dir %{_datadir}/lxc/config/common.conf.d
%{_datadir}/lxc/config/common.conf.d/00-lxcfs.conf
%attr(755,root,root) %{_libdir}/%{name}/liblxcfs.so

