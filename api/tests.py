from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.test import SimpleTestCase
from rest_framework.test import APISimpleTestCase
from api.algorithms import worldPopulationRankByDate, dateByWorldPopulationRank, lifeExpectancyRemaining, populationCount
from api.datastore import dataStore
from api.exceptions import *



class TestAlgorithm(SimpleTestCase):
    """
    Tests the various calculation functions. All the reference values have been generated with the original R script (see modeling/R/).
    """

    DELTA = 1000000

    def test_regions(self):
        self.assertTrue(len(dataStore.countries) > 200)
        self.assertTrue('World' in dataStore.countries)
        self.assertTrue('Estonia' in dataStore.countries)
        self.assertTrue('Reunion' in dataStore.countries)

    def test_byDate_today(self):
        self.assertAlmostEqual(56598000,   worldPopulationRankByDate('unisex', 'World', date(2013, 12, 31), date(2014,  6,  1)), delta=TestAlgorithm.DELTA)
        self.assertAlmostEqual(2541178000, worldPopulationRankByDate('unisex', 'World', date(1993, 12,  6), date(2014,  6,  1)), delta=TestAlgorithm.DELTA)
        self.assertAlmostEqual(4178250000, worldPopulationRankByDate('unisex', 'World', date(1980,  1,  1), date(2014,  6,  1)), delta=TestAlgorithm.DELTA)
        self.assertAlmostEqual(5989238000, worldPopulationRankByDate('unisex', 'World', date(1960,  2, 29), date(2014,  6,  1)), delta=TestAlgorithm.DELTA)
        self.assertAlmostEqual(7233264000, worldPopulationRankByDate('unisex', 'World', date(1920,  1,  1), date(2014,  6,  1)), delta=TestAlgorithm.DELTA)

    def test_byDate_age(self):
        self.assertAlmostEqual(2541533000, worldPopulationRankByDate('unisex', 'World', date(1993, 12,  6), date(1993, 12,  6) + timedelta(days=7483)), delta=TestAlgorithm.DELTA)
        self.assertAlmostEqual(1209918000, worldPopulationRankByDate('unisex', 'World', date(1993, 12,  6), date(1993, 12,  6) + timedelta(days=3650)), delta=TestAlgorithm.DELTA)
        self.assertAlmostEqual(578344100,  worldPopulationRankByDate('unisex', 'World', date(1940,  5,  3), date(1940,  5,  3) + timedelta(days=3530)), delta=TestAlgorithm.DELTA)
        self.assertAlmostEqual(217482,     worldPopulationRankByDate('unisex', 'World', date(1950,  1,  1), date(1950,  1,  1) + timedelta(days=0)),    delta=TestAlgorithm.DELTA)

    def test_byDate_date(self):
        self.assertAlmostEqual(940947000,  worldPopulationRankByDate('unisex', 'World', date(1993, 12,  6), date(2001,  9, 11)), delta=TestAlgorithm.DELTA)
        self.assertAlmostEqual(7198923000, worldPopulationRankByDate('unisex', 'World', date(1920,  1,  1), date(2014,  1,  1)), delta=TestAlgorithm.DELTA)

    def test_byDate_invalidSex(self):
        self.assertRaises(InvalidSexError, worldPopulationRankByDate, 'INVALID', 'World', date(1980, 1, 1), date(2000, 1, 1))

    def test_byDate_invalidRegion(self):
        self.assertRaises(InvalidCountryError, worldPopulationRankByDate, 'unisex', 'THIS COUNTRY DOES NOT EXIST', date(1980, 1, 1), date(2000, 1, 1))

    def test_byDate_dobOutOfRange(self):
        self.assertRaises(BirthdateOutOfRangeError, worldPopulationRankByDate, 'unisex', 'World', date(1915, 1, 1), date(2000, 1, 1))
        self.assertRaises(BirthdateOutOfRangeError, worldPopulationRankByDate, 'unisex', 'World', date(2030, 1, 1), date(2000, 1, 1))

    def test_byDate_dateOutOfRange(self):
        self.assertRaises(CalculationDateOutOfRangeError, worldPopulationRankByDate, 'unisex', 'World', date(1945, 1, 1), date(1949, 1, 1))
        self.assertRaises(CalculationDateOutOfRangeError, worldPopulationRankByDate, 'unisex', 'World', date(1970, 1, 1), date(1960, 1, 1))

    def test_byDate_calculationTooWide(self):
        self.assertRaises(CalculationTooWideError, worldPopulationRankByDate, 'unisex', 'World', date(1930, 1, 1), date(2031, 1, 1))

    def test_byRank(self):
        self.assertEqual(date(2049,  3, 11), dateByWorldPopulationRank('unisex', 'World', date(1993, 12,  6), 7000000000))

    def test_lifeExpectancy(self):
        self.assertAlmostEqual(26.24, lifeExpectancyRemaining('unisex', 'World', date(2049, 3, 11), relativedelta(years=55, months=4)), places=0)
        self.assertAlmostEqual(28.05, lifeExpectancyRemaining('male', 'UK', date(2001, 5, 11), relativedelta(years=49)), places=0)

    def test_population(self):
        data = list(populationCount('Brazil', 18, 1980))
        self.assertEqual(1, len(data))
        self.assertEqual(2719710, data[0]['total'])
        data = list(populationCount('Brazil', 18))
        self.assertEqual(151, len(data))
        self.assertEqual(1980, data[30]['year'])
        self.assertEqual(2719710, data[30]['total'])



class TestViews(APISimpleTestCase):
    def _testEndpoint(self, path, expectErrorContaining=None):
        response = self.client.get('/1.0' + path)
        if expectErrorContaining:
            self.assertEqual(response.status_code, 400)
            self.assertTrue(expectErrorContaining in response.data['detail'], 'Expected fragment "%s" in error message: %s' % (expectErrorContaining, response.data['detail']))
        else:
            self.assertEqual(response.status_code, 200)

    def testRankEndpointToday_success(self):
        self._testEndpoint('/wp-rank/1952-03-11/unisex/World/today/')

    def testRankEndpointToday_invalidSex(self):
        self._testEndpoint('/wp-rank/1952-03-11/123/World/today/', expectErrorContaining='sex')

    def testRankEndpointToday_invalidCountry(self):
        self._testEndpoint('/wp-rank/1952-03-11/unisex/123/today/', expectErrorContaining='country')

    def testRankEndpointAged_successWithDays(self):
        self._testEndpoint('/wp-rank/1952-03-11/unisex/World/aged/123/',)

    def testRankEndpointAged_successWithOffset(self):
        self._testEndpoint('/wp-rank/1952-03-11/unisex/World/aged/12y34m56d/')

    def testRankEndpointAged_invalidOffset(self):
        self._testEndpoint('/wp-rank/1952-03-11/unisex/World/aged/5x/', expectErrorContaining='offset')

    def testPopulationEndpoint_successCountryAndAgeOnly(self):
        self._testEndpoint('/population/Brazil/18/')

    def testPopulationEndpoint_successYearCountryAndAge(self):
        self._testEndpoint('/population/1980/Brazil/18/')

    def testPopulationEndpoint_successYearAndCountryOnly(self):
        self._testEndpoint('/population/1980/Brazil/')

    def testLifeExpectancyRemainingEndpoint_successMaxDate(self):
        self._testEndpoint('/life-expectancy/remaining/unisex/World/2094-12-31/100y/')

    def testLifeExpectancyRemainingEndpoint_exceedMaxDate(self):
        self._testEndpoint('/life-expectancy/remaining/unisex/World/2095-01-01/100y/', expectErrorContaining='calculation date')

    def testLifeExpectancyRemainingEndpoint_exceedAge(self):
        self._testEndpoint('/life-expectancy/remaining/unisex/World/2094-12-31/100y1d/', expectErrorContaining='age')

    def testLifeExpectancyRemainingEndpoint_successMinDate(self):
        self._testEndpoint('/life-expectancy/remaining/unisex/World/1955-01-01/1/')

    def testLifeExpectancyRemainingEndpoint_belowMinDate(self):
        self._testEndpoint('/life-expectancy/remaining/unisex/World/1954-12-31/1/', expectErrorContaining='calculation date')

    def testLifeExpectancyRemainingEndpoint_exceedAgeAtMinDate(self):
        self._testEndpoint('/life-expectancy/remaining/unisex/World/1955-01-01/100y1d/', expectErrorContaining='age')

    def testLifeExpectancyTotalEndpoint_successMinBirthdate(self):
        self._testEndpoint('/life-expectancy/total/unisex/World/1920-01-01/')

    def testLifeExpectancyTotalEndpoint_belowMinBirthdate(self):
        self._testEndpoint('/life-expectancy/total/unisex/World/1919-12-31/', expectErrorContaining='birthdate')

    def testLifeExpectancyTotalEndpoint_successMaxBirthdate(self):
        self._testEndpoint('/life-expectancy/total/unisex/World/2059-12-31/')

    def testLifeExpectancyTotalEndpoint_exceedMaxBirthdate(self):
        self._testEndpoint('/life-expectancy/total/unisex/World/2060-01-01/', expectErrorContaining='birthdate')
