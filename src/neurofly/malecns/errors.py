"""Phase 1A failure types with credential-safe messages."""


class MaleCNSError(RuntimeError):
    """Base error for the MaleCNS slice."""


class MaleCNSAccessError(MaleCNSError):
    """Authentication, service, or dataset access failed."""


class MaleCNSDataError(MaleCNSError):
    """Retrieved data could not be normalized safely."""


class MaleCNSValidationError(MaleCNSError):
    """Pinned scientific invariants did not hold."""


class SnapshotExportError(MaleCNSError):
    """A local derived snapshot could not be exported safely."""


class SnapshotIntegrityError(MaleCNSError):
    """An offline snapshot does not match its manifest or file schema."""
