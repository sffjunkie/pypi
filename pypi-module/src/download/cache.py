from cachecontrol.caches import FileCache


class SafeFileCache(FileCache):
    """
    A file based cache which is safe to use even when the target directory may
    not be accessible or writable.
    """

    def __init__(self, *args, **kwargs):
        super(SafeFileCache, self).__init__(*args, **kwargs)

        # Check to ensure that the directory containing our cache directory
        # is owned by the user current executing pip. If it does not exist
        # we will check the parent directory until we find one that does exist.
        # If it is not owned by the user executing pip then we will disable
        # the cache and log a warning.
        if not check_path_owner(self.directory):
            logger.warning(
                "The directory '%s' or its parent directory is not owned by "
                "the current user and the cache has been disabled. Please "
                "check the permissions and owner of that directory. If "
                "executing pip with sudo, you may want sudo's -H flag.",
                self.directory,
            )

            # Set our directory to None to disable the Cache
            self.directory = None

    def get(self, *args, **kwargs):
        # If we don't have a directory, then the cache should be a no-op.
        if self.directory is None:
            return

        try:
            return super(SafeFileCache, self).get(*args, **kwargs)
        except (LockError, OSError, IOError):
            # We intentionally silence this error, if we can't access the cache
            # then we can just skip caching and process the request as if
            # caching wasn't enabled.
            pass

    def set(self, *args, **kwargs):
        # If we don't have a directory, then the cache should be a no-op.
        if self.directory is None:
            return

        try:
            return super(SafeFileCache, self).set(*args, **kwargs)
        except (LockError, OSError, IOError):
            # We intentionally silence this error, if we can't access the cache
            # then we can just skip caching and process the request as if
            # caching wasn't enabled.
            pass

    def delete(self, *args, **kwargs):
        # If we don't have a directory, then the cache should be a no-op.
        if self.directory is None:
            return

        try:
            return super(SafeFileCache, self).delete(*args, **kwargs)
        except (LockError, OSError, IOError):
            # We intentionally silence this error, if we can't access the cache
            # then we can just skip caching and process the request as if
            # caching wasn't enabled.
            pass

