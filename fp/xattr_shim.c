/* Workaround für bubblewrap 0.12.0 + SELinux: lsetxattr auf security.* ignorieren.
 * Kompilieren: gcc -shared -fPIC -o xattr_shim.so xattr_shim.c -ldl
 * Verwenden:   LD_PRELOAD=/path/to/xattr_shim.so flatpak-builder ...
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <string.h>
#include <errno.h>
#include <sys/xattr.h>

int lsetxattr(const char *path, const char *name, const void *value, size_t size, int flags) {
    static int (*real_lsetxattr)(const char*, const char*, const void*, size_t, int) = NULL;
    if (!real_lsetxattr)
        real_lsetxattr = dlsym(RTLD_NEXT, "lsetxattr");
    int ret = real_lsetxattr(path, name, value, size, flags);
    if (ret != 0 && strncmp(name, "security.", 9) == 0) {
        errno = 0;
        return 0;
    }
    return ret;
}
