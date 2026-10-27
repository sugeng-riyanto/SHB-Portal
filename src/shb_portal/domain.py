"""Pure, framework-independent financial and authorization rules.

Amounts are integer IDR. Callers must fetch membership from a trusted source.
These functions do not implement login, persistence, or database security.
"""
from dataclasses import dataclass
from datetime import date
from enum import Enum

class Role(str, Enum):
    ADMIN = 'admin'
    PRINCIPAL = 'principal'
    FOUNDATION = 'foundation'
    TEACHER = 'teacher'
    GUARDIAN = 'guardian'

@dataclass(frozen=True)
class Scope:
    school_id: str
    classes: frozenset[str] = frozenset()
    children: frozenset[str] = frozenset()

@dataclass(frozen=True)
class Invoice:
    school_id: str
    student_id: str
    class_id: str
    principal: int
    fine: int
    paid: int
    due_date: date
    cancelled: bool = False

    def __post_init__(self):
        for value in (self.principal, self.fine, self.paid):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError('Amounts must be nonnegative integer IDR')
        if self.paid > self.principal + self.fine:
            raise ValueError('Overpayment requires an explicit policy')

    @property
    def balance(self):
        return self.principal + self.fine - self.paid

    def status(self, today: date):
        if self.cancelled:
            return 'cancelled'
        if self.balance == 0:
            return 'paid'
        if today > self.due_date:
            return 'overdue'
        if self.paid:
            return 'partial'
        return 'unpaid'

    def reminder_due(self, today: date, days_before: int):
        if isinstance(days_before, bool) or not isinstance(days_before, int) or days_before < 0:
            raise ValueError('days_before must be a nonnegative integer')
        return not self.cancelled and self.balance > 0 and 0 <= (self.due_date - today).days <= days_before

def can_view_invoice(role: Role, scope: Scope, invoice: Invoice):
    """Individual invoices are limited to admin, assigned teacher, or linked guardian."""
    if scope.school_id != invoice.school_id:
        return False
    if role == Role.ADMIN:
        return True
    if role == Role.TEACHER:
        return invoice.class_id in scope.classes
    if role == Role.GUARDIAN:
        return invoice.student_id in scope.children
    return False

def can_preview_proof(role: Role, scope: Scope, invoice: Invoice, owner_id: str, user_id: str):
    if scope.school_id != invoice.school_id:
        return False
    if role in (Role.ADMIN, Role.PRINCIPAL):
        return True
    if role == Role.TEACHER:
        return invoice.class_id in scope.classes
    if role == Role.GUARDIAN:
        return owner_id == user_id and invoice.student_id in scope.children
    return False
