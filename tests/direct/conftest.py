"""Windows compatibility for genlayer-test's Direct Mode stdin temp-file cleanup."""
import os
import pytest


@pytest.fixture(autouse=True)
def fix_direct_mode_windows_tempfile_cleanup(direct_vm, monkeypatch):
    """Defer unlink until VM restores fd 0; Windows cannot unlink an open file."""
    if os.name != 'nt':
        return
    from gltest.direct import loader

    deferred_paths = []
    original_inject = loader._inject_message_to_fd0
    original_unlink = os.unlink
    original_cleanup = direct_vm._cleanup_after_deactivate

    def inject_with_deferred_unlink(vm):
        def unlink_after_fd_restore(path, *args, **kwargs):
            try:
                return original_unlink(path, *args, **kwargs)
            except PermissionError:
                deferred_paths.append(path)
                return None

        with monkeypatch.context() as patcher:
            patcher.setattr(os, 'unlink', unlink_after_fd_restore)
            return original_inject(vm)

    def cleanup_then_unlink():
        original_cleanup()
        while deferred_paths:
            path = deferred_paths.pop()
            try:
                original_unlink(path)
            except FileNotFoundError:
                pass

    monkeypatch.setattr(loader, '_inject_message_to_fd0', inject_with_deferred_unlink)
    monkeypatch.setattr(direct_vm, '_cleanup_after_deactivate', cleanup_then_unlink)
