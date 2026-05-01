class ControlExecutor:
    def __init__(self, dry_run: bool = True) -> None:
        self.dry_run = dry_run

    def execute(self, action: str) -> None:
        if self.dry_run:
            print(f"[DRY-RUN] {action}")
            return
        raise NotImplementedError("Real input execution is disabled by default")
