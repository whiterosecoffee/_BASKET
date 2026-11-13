"""Independent-review F1 regressions: reject invalid budgets before access."""
import unittest
from decimal import Decimal
from datetime import datetime
from unittest.mock import patch
from runtime.massive_maintainer import maintain as m
from runtime.massive_maintainer import test_eligibility as fixtures

class FreshnessContractTests(unittest.TestCase):
    setUp=fixtures.EligibilityTests.setUp
    coverage=fixtures.EligibilityTests.coverage
    publish=fixtures.EligibilityTests.publish
    invalid=(True,False,None,'1200',float('nan'),float('inf'),-float('inf'),-1,0,1201,10**400,Decimal('5'))
    def assert_contract_error(self,call):
        with self.assertRaises(ValueError) as error:call()
        self.assertEqual(getattr(error.exception,'code',None),'invalid_freshness_budget')
        self.assertEqual(getattr(error.exception,'field',None),'max_age_seconds')
    def test_resolver_invalid_before_reads_or_requests(self):
        for value in self.invalid:
            with self.subTest(value=str(value)):
                with patch.object(m,'read',side_effect=AssertionError('read before validation')) as reader,patch.object(m,'atomic',side_effect=AssertionError('write before validation')):
                    self.assert_contract_error(lambda:m.resolve(self.pointer,'NVDA',self.day,self.t,max_age_seconds=value))
                    reader.assert_not_called()
    def test_direct_gate_and_request_boundaries(self):
        for value in self.invalid:
            with self.subTest(value=str(value)),patch.object(m,'read',side_effect=AssertionError('data access')):
                self.assert_contract_error(lambda:m.current_ineligibility(self.root,{},self.day,self.t,value,None))
                request={'ticker':'NVDA','date':self.day,'required_through':self.t,'max_age_seconds':value}
                self.assert_contract_error(lambda:m.validate_request(request))
                self.assert_contract_error(lambda:m.fulfilled_request_is_current(self.root,request))
    def test_stale_observations_and_infinity_bypass(self):
        clock=datetime.fromtimestamp((self.t+86400000)/1000,m.UTC).isoformat()
        with patch.object(m,'now',return_value=clock):
            self.ev=[{'fetched_at':clock,'sha256':'fixture'}];self.publish()
            self.assertEqual(m.resolve(self.pointer,'NVDA',self.day,self.t+120000,coverage=self.coverage())['reason'],'stale_observation')
            self.assert_contract_error(lambda:m.resolve(self.pointer,'NVDA',self.day,self.t+120000,max_age_seconds=float('inf'),coverage=self.coverage()))
            self.assertEqual(m.resolve(self.pointer,'NVDA',self.day)['status'],'qualified_historical')
    def test_finite_positive_current_control(self):
        clock=datetime.fromtimestamp((self.t+180000)/1000,m.UTC).isoformat()
        with patch.object(m,'now',return_value=clock):
            self.ev=[{'fetched_at':clock,'sha256':'fixture'}];self.publish()
            for budget in (0.5,1,1200):
                with self.subTest(budget=budget):
                    self.assertEqual(m.resolve(self.pointer,'NVDA',self.day,self.t+120000,max_age_seconds=budget,coverage=self.coverage())['status'],'qualified_current')
