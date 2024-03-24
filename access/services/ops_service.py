from uuid import UUID, uuid4
from typing import Callable
from datetime import datetime
from ..models import Operation
from ..scheduler import scheduler, DateTrigger


class OperationsService:

    def __init__(self):
        self.operations: dict[UUID, Operation] = {}

    def execute_operation(
        self,
        func: Callable,
        run_date: datetime | str = None,
        args: list | tuple = (),
    ) -> UUID:
        op_id = uuid4()
        self.operations[op_id] = Operation(op_id)

        def __exec_func() -> None:
            res = func(*args)
            self.finish_operation(op_id, res)

        scheduler.add_job(
            __exec_func,
            trigger=DateTrigger(datetime.now() if run_date is None else run_date),
        )
        return op_id

    def finish_operation(self, op_id: UUID, result) -> bool:
        op: Operation = self.operations.get(op_id)
        if op is None:
            return False
        op.result = result
        op.done = True
        return True

    def get_operation(self, op_id: UUID) -> Operation | None:
        return self.operations.get(op_id)
