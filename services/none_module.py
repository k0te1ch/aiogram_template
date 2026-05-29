from loguru import logger


class _NotDefinedModuleError(Exception):
    pass


class _NoneModule:
    """Placeholder for an optional service that wasn't configured.

    Accessing any attribute/item raises a descriptive error, so a missing
    REDIS_URL/DATABASE_URL fails loudly at first use instead of silently.
    """

    def __init__(self, module_name: str, attr_name: str) -> None:
        self.module_name = module_name
        self.attr_name = attr_name

    def __getitem__(self, item) -> _NotDefinedModuleError:
        msg = f"You are using {self.module_name} while {self.attr_name} is not set in config"
        logger.critical(msg)
        raise _NotDefinedModuleError(msg)

    def __getattr__(self, attr) -> _NotDefinedModuleError:
        msg = f"You are using {self.module_name} while {self.attr_name} is not set in config"
        logger.critical(msg)
        raise _NotDefinedModuleError(msg)
