class RevenueToolError(Exception):
    """Base error shown to the operator without a traceback."""


class InputValidationError(RevenueToolError):
    """The workbook or configuration does not meet the input contract."""


class UnknownTradeTypeError(RevenueToolError):
    """No transit cycle could be resolved for a shipment trade type."""

