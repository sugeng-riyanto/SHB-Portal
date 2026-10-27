import unittest
from datetime import date
from shb_portal.domain import Invoice, Role, Scope, can_view_invoice, can_preview_proof

class DomainTests(unittest.TestCase):
    def setUp(self):
        self.invoice = Invoice('s1', 'child1', '8A', 500000, 10000, 100000, date(2026, 11, 10))
    def test_balance_and_status(self):
        self.assertEqual(self.invoice.balance, 410000)
        self.assertEqual(self.invoice.status(date(2026, 11, 9)), 'partial')
        self.assertEqual(self.invoice.status(date(2026, 11, 11)), 'overdue')
    def test_paid_cancelled_and_reminders(self):
        paid = Invoice('s1','child1','8A', 100,0,100,date(2026,11,10))
        cancelled = Invoice('s1','child1','8A',100,0,0,date(2026,11,10),True)
        self.assertFalse(paid.reminder_due(date(2026,11,9),7))
        self.assertFalse(cancelled.reminder_due(date(2026,11,9),7))
        self.assertTrue(self.invoice.reminder_due(date(2026,11,3),7))
        self.assertFalse(self.invoice.reminder_due(date(2026,11,2),7))
    def test_integer_and_overpayment(self):
        for value in (-1, 1.5, True):
            with self.assertRaises(ValueError): Invoice('s','c','x',value,0,0,date.today())
        with self.assertRaises(ValueError): Invoice('s','c','x',10,0,11,date.today())
    def test_guardian_and_teacher_scope(self):
        self.assertTrue(can_view_invoice(Role.GUARDIAN, Scope('s1', children=frozenset({'child1','child2'})),self.invoice))
        self.assertFalse(can_view_invoice(Role.GUARDIAN, Scope('s1', children=frozenset({'child2'})),self.invoice))
        self.assertFalse(can_view_invoice(Role.TEACHER, Scope('s1', classes=frozenset({'8B'})),self.invoice))
        self.assertFalse(can_view_invoice(Role.ADMIN, Scope('other'),self.invoice))
        self.assertFalse(can_view_invoice(Role.FOUNDATION, Scope('s1'),self.invoice))
    def test_proof_ownership_and_scope(self):
        guardian = Scope('s1',children=frozenset({'child1'}))
        self.assertTrue(can_preview_proof(Role.GUARDIAN, guardian, self.invoice, 'u1','u1'))
        self.assertFalse(can_preview_proof(Role.GUARDIAN, guardian, self.invoice, 'u2','u1'))
        self.assertTrue(can_preview_proof(Role.PRINCIPAL, Scope('s1'), self.invoice, 'u1','p1'))
        self.assertFalse(can_preview_proof(Role.PRINCIPAL, Scope('s2'), self.invoice, 'u1','p1'))
if __name__ == '__main__': unittest.main()
