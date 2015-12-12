from datetime import date, timedelta
from unittest.case import skip
from dateutil.relativedelta import relativedelta
from django.test import SimpleTestCase
from rest_framework.test import APISimpleTestCase
from api.algorithms import worldPopulationRankByDate, dateByWorldPopulationRank, lifeExpectancyRemaining, populationCount, \
    lifeExpectancyTotal, totalPopulation, calculateMortalityDistribution
from api.datastore import dataStore
from api.exceptions import *



class AlgorithmTests(SimpleTestCase):
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
        self.assertAlmostEqual(56598000,   worldPopulationRankByDate('unisex', 'World', date(2013, 12, 31), date(2014,  6,  1)), delta=AlgorithmTests.DELTA)
        self.assertAlmostEqual(2541178000, worldPopulationRankByDate('unisex', 'World', date(1993, 12,  6), date(2014,  6,  1)), delta=AlgorithmTests.DELTA)
        self.assertAlmostEqual(4178250000, worldPopulationRankByDate('unisex', 'World', date(1980,  1,  1), date(2014,  6,  1)), delta=AlgorithmTests.DELTA)
        self.assertAlmostEqual(5989238000, worldPopulationRankByDate('unisex', 'World', date(1960,  2, 29), date(2014,  6,  1)), delta=AlgorithmTests.DELTA)
        self.assertAlmostEqual(7233264000, worldPopulationRankByDate('unisex', 'World', date(1920,  1,  1), date(2014,  6,  1)), delta=AlgorithmTests.DELTA)

    def test_byDate_age(self):
        self.assertAlmostEqual(2541533000, worldPopulationRankByDate('unisex', 'World', date(1993, 12,  6), date(1993, 12,  6) + timedelta(days=7483)), delta=AlgorithmTests.DELTA)
        self.assertAlmostEqual(1209918000, worldPopulationRankByDate('unisex', 'World', date(1993, 12,  6), date(1993, 12,  6) + timedelta(days=3650)), delta=AlgorithmTests.DELTA)
        self.assertAlmostEqual(578344100,  worldPopulationRankByDate('unisex', 'World', date(1940,  5,  3), date(1940,  5,  3) + timedelta(days=3530)), delta=AlgorithmTests.DELTA)
        self.assertAlmostEqual(217482,     worldPopulationRankByDate('unisex', 'World', date(1950,  1,  1), date(1950,  1,  1) + timedelta(days=0)),    delta=AlgorithmTests.DELTA)

    def test_byDate_date(self):
        self.assertAlmostEqual(940947000,  worldPopulationRankByDate('unisex', 'World', date(1993, 12,  6), date(2001,  9, 11)), delta=AlgorithmTests.DELTA)
        self.assertAlmostEqual(7198923000, worldPopulationRankByDate('unisex', 'World', date(1920,  1,  1), date(2014,  1,  1)), delta=AlgorithmTests.DELTA)

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

    def test_byRank_veryLowRank(self):
        self.assertEqual(date(2004, 11, 22), dateByWorldPopulationRank('female', 'World', date(2004, 11, 22), 10000))
        self.assertEqual(date(2014,  1,  1), dateByWorldPopulationRank('male',   'World', date(2014,  1,  1), 300))

    def test_byRank_veryHighRank(self):
        self.assertEqual(date(2027, 11, 29), dateByWorldPopulationRank('unisex', 'World', date(2004, 11, 22), 3000000000))

    def test_lifeExpectancyRemaining(self):
        self.assertAlmostEqual(28.53, lifeExpectancyRemaining('female', 'World', date(2049, 3, 11), relativedelta(years=55, months=4)), places=0)
        self.assertAlmostEqual(32.80, lifeExpectancyRemaining('male', 'United Kingdom', date(2001, 5, 11), relativedelta(years=49)), places=0)

    def test_lifeExpectancyRemaining_maxAge(self):
        self.assertAlmostEqual(1.12, lifeExpectancyRemaining('female', 'Afghanistan', date(1955, 1, 1), relativedelta(years=120)), places=0)
        self.assertAlmostEqual(1.12, lifeExpectancyRemaining('male', 'United Kingdom', date(2050, 1, 1), relativedelta(years=120)), places=0)

    def test_lifeExpectancyTotal(self):
        self.assertAlmostEqual(90.34, lifeExpectancyTotal('female', 'World', date(2015, 6, 30)), places=0)

    def test_population(self):
        data = list(populationCount('Brazil', 18, 1980))
        self.assertEqual(1, len(data))
        self.assertEqual(2719710, data[0]['total'])
        data = list(populationCount('Brazil', 18))
        self.assertEqual(151, len(data))
        self.assertEqual(1980, data[30]['year'])
        self.assertEqual(2719710, data[30]['total'])

    def test_total_population(self):
        self.assertEqual(totalPopulation('United Kingdom', date(2013, 1, 1)), 62961264)
        self.assertEqual(totalPopulation('Afghanistan', date(2022, 12, 31)), 37599673)
        self.assertEqual(totalPopulation('World', date(2018, 7, 31)), 7569167368)

    def test_mortality_distribution(self):
        self.assertEqual(calculateMortalityDistribution('Germany', 'male', relativedelta(years=43, months=3))[3][1],2.2179399450663992)


class ApiIntegrationTests(APISimpleTestCase):
    """
    A set of test cases testing the whole stack, from the url routing to the request processing to delivering the right status code. Do not check any returned data.
    """

    def setUp(self):
        super(ApiIntegrationTests, self).setUp()
        # set a valid authorization header
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + 'sf8sf9g-91e2-11e5-8994-feff819cdc9f')


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
        self._testEndpoint('/wp-rank/1952-03-11/male/United%20Kingdom/aged/49y2m/')

    def testRankEndpointAged_invalidOffset(self):
        self._testEndpoint('/wp-rank/1952-03-11/unisex/World/aged/5x/', expectErrorContaining='offset')

    def testPopulationEndpoint_successCountryAndAgeOnly(self):
        self._testEndpoint('/population/Brazil/18/')

    def testPopulationEndpoint_successYearCountryAndAge(self):
        self._testEndpoint('/population/1980/Brazil/18/')

    def testPopulationEndpoint_successYearAndCountryOnly(self):
        self._testEndpoint('/population/1980/Brazil/')

    def testPopulationEndpoint_totalPopulation(self):
        self._testEndpoint('/population/Brazil/today-and-tomorrow/')
        self._testEndpoint('/population/United%20Kingdom/2015-11-12/')

    def testPopulationEndpoint_totalPopulation_outOfRange(self):
        self._testEndpoint('/population/Brazil/2012-12-31/', expectErrorContaining='calculation date')
        self._testEndpoint('/population/Brazil/2023-01-01/', expectErrorContaining='calculation date')

    def testLifeExpectancyRemainingEndpoint_successMaxDate(self):
        self._testEndpoint('/life-expectancy/remaining/female/World/2094-12-31/100y/')

    def testLifeExpectancyRemainingEndpoint_exceedMaxDate(self):
        self._testEndpoint('/life-expectancy/remaining/female/World/2095-01-01/100y/', expectErrorContaining='calculation date')

    def testLifeExpectancyRemainingEndpoint_successMaxAge(self):
        self._testEndpoint('/life-expectancy/remaining/male/Afghanistan/1990-01-01/120y/')

    def testLifeExpectancyRemainingEndpoint_exceedAge(self):
        self._testEndpoint('/life-expectancy/remaining/female/World/2094-12-31/120y1d/', expectErrorContaining='age')

    def testLifeExpectancyRemainingEndpoint_exceedAgeFuture(self):
        self._testEndpoint('/life-expectancy/remaining/female/World/2094-12-31/120y1d/', expectErrorContaining='age')

    def testLifeExpectancyRemainingEndpoint_successMinDate(self):
        self._testEndpoint('/life-expectancy/remaining/female/World/1955-01-01/1/')

    def testLifeExpectancyRemainingEndpoint_belowMinDate(self):
        self._testEndpoint('/life-expectancy/remaining/female/World/1954-12-31/1/', expectErrorContaining='calculation date')

    def testLifeExpectancyRemainingEndpoint_exceedAgeAtMinDate(self):
        self._testEndpoint('/life-expectancy/remaining/female/World/1955-01-01/120y1d/', expectErrorContaining='age')

    def testLifeExpectancyRemainingEndpoint_successMaxBirthdate(self):
        self._testEndpoint('/life-expectancy/remaining/female/World/2015-06-30/1/')

    def testLifeExpectancyRemainingEndpoint_exceedMaxBirthdate(self):
        self._testEndpoint('/life-expectancy/remaining/female/World/2015-07-02/1/', expectErrorContaining='birthdate')

    def testLifeExpectancyTotalEndpoint_successMinBirthdate(self):
        self._testEndpoint('/life-expectancy/total/female/World/1920-01-01/')

    def testLifeExpectancyTotalEndpoint_belowMinBirthdate(self):
        self._testEndpoint('/life-expectancy/total/female/World/1919-12-31/', expectErrorContaining='birthdate')

    def testLifeExpectancyTotalEndpoint_successMaxBirthdate(self):
        self._testEndpoint('/life-expectancy/total/female/World/2015-06-30/')

    def testLifeExpectancyTotalEndpoint_exceedMaxBirthdate(self):
        self._testEndpoint('/life-expectancy/total/female/World/2015-07-01/', expectErrorContaining='birthdate')

    def testMortalityDistribution(self):
        self._testEndpoint('/mortality-distribution/United%20Kingdom/male/49y2m/today/')


@skip
class AlgorithmAcceptanceTests(SimpleTestCase):
    """
    A set of tests based on the acceptance tests previously written in R.
    """

    CNTRY = 'World'
    iSEX = 'unisex'
    TODAY = date(2014, 9, 15)

    def yourRANKToday(self, DoB):   # Helper function to make this test case look as closely as the R acceptance test as possible
        return worldPopulationRankByDate(self.iSEX, self.CNTRY, DoB, self.TODAY) / 1000

    def yourRANKbyAge(self, DoB, iAge):   # Helper function to make this test case look as closely as the R acceptance test as possible
        return worldPopulationRankByDate(self.iSEX, self.CNTRY, DoB, self.TODAY - relativedelta(days=iAge)) / 1000

    def yourRANKbyDate(self, DoB, refdate):   # Helper function to make this test case look as closely as the R acceptance test as possible
        return worldPopulationRankByDate(self.iSEX, self.CNTRY, DoB, refdate) / 1000

    def rem_le(self, le_date, le_exact_age):
        return lifeExpectancyRemaining('male', self.CNTRY, le_date, le_exact_age)

    def test_yourRANKToday_success(self):
        # line 12: yourRANKToday(DoB) #my ranking today: 2578836
        self.assertAlmostEqual(self.yourRANKToday(DoB=date(1993, 12, 6)), 2578836, delta=5)

    def test_yourRANKbyAge_success(self):
        # line 13: yourRANKbyAge(DoB=DoB,iAge=as.numeric(Sys.Date()-as.Date(DoB,"%Y/%m/%d"))) #my ranking at today's age: 2578836
        iAge = (self.TODAY - date(1993, 12, 6)).days
        self.assertAlmostEqual(self.yourRANKbyAge(DoB=date(1993, 12, 6), iAge=iAge), 2578836, delta=5)

    def test_yourRANKbyAge_successTenYearsOld(self):
        # line 14: yourRANKbyAge(DoB=DoB,iAge=3650) #my ranking when I was 10 years old (3650 days) : 1209918
        self.assertAlmostEqual(self.yourRANKbyAge(DoB=date(1993, 12, 6), iAge=3650), 1209918, delta=5)

    def test_yourRANKbyDate_success(self):
        # line 15: yourRANKbyDate(DoB,"2001/9/11") #my ranking on 11th Sept 2001 :940947
        self.assertAlmostEqual(self.yourRANKbyDate(DoB=date(1993, 12, 6), refdate=date(2011, 9, 11)), 940947, delta=5)

    # line 28: DoB = "1920/1/1"

    def test_yourRANKbyDate_belowMinDate(self):
        # line 19: yourRANKbyDate(DoB,"1949/12/31") #my ranking on 31st Dec 1949 :ERROR Data not available
        with self.assertRaises(CalculationDateOutOfRangeError):
            self.yourRANKbyDate(DoB=date(1920, 1, 1), refdate=date(1949, 12, 31))

    def test_yourRANKbyDate_atMinDate(self):
        # line 20: yourRANKbyDate(DoB,"1950/01/01") #1506711 #my ranking on 1st Jan 1950: minimum Date for which rank can be reported
        self.assertAlmostEqual(self.yourRANKbyDate(DoB=date(1920, 1, 1), refdate=date(1950, 1, 1)), 1506711, delta=5)

    def test_yourRANKbyDate_tooOld(self):
        # skipped line 22, as it appears to be incompletely written, as it is a subset of line 23
        # line 23: yourRANKbyDate(DoB,"2019/12/8") #NA #if you are more than 36500 days older then you are too old to report exact rank
        with self.assertRaises(CalculationTooWideError):
            self.yourRANKbyDate(DoB=date(1920, 1, 1), refdate=date(2019, 12, 8))

    # line 29: DoB = "2020/12/31"

    def test_yourRANKbyDate_notBornYet(self):   # hheimbuerger: this test would imply that the DoB can never be before the reference date, yet that's exactly what 'successFuture'
                                                #               from line 31 tests for -- I don't understand how I'm supposed to make both pass!
        # line 30: yourRANKToday(DoB) #NA #because the person is not born yet
        with self.assertRaises(BirthdateOutOfRangeError):
            self.yourRANKToday(DoB=date(2020, 12, 31))

    def test_yourRANKbyDate_successFuture(self):
        # line 31: yourRANKbyDate(DoB,"2021/12/31") #133045.1
        self.assertAlmostEqual(self.yourRANKbyDate(DoB=date(2020, 12, 31), refdate=date(2021, 12, 31)), 133045.1, delta=5)

    # line 33: DoB = "2100/12/31" #maximum DoB

    def test_yourRANKToday_beyondMaxBirthdate(self):   # hheimbuerger: I don't understand why this test is expected to fail, line 33 declares 2100-12-31 the maximum DoB
        # line 34: yourRANKToday(DoB) #NA
        with self.assertRaises(BirthdateOutOfRangeError):
            self.yourRANKToday(DoB=date(2100, 12, 31))

    def test_yourRANKbyDate_atMaxDate(self):
        # line 35: yourRANKbyDate(DoB,"2100/12/31") #349.4013 #Also maximum Date that a rank can be reported...
        self.assertAlmostEqual(self.yourRANKbyDate(DoB=date(2100, 12, 31), refdate=date(2100, 12, 31)), 349.4013, delta=5)

    # line 37: DoB = "1920/1/1" #minimum DoB (it is possible for DoB few years earlier but I suggest to start at 1920, for older cohorts, we put a message that the person is too old for and report the rank of the person born on 1920/1/1, saying your rank is higher than the rank for 1920/1/1 )

    def test_yourRANKToday_belowMinBirthdate(self):   # hheimbuerger: I don't understand why this test is expected to fail, line 37 declares 1920-01-01 the minimum DoB
        # line 38: yourRANKToday(DoB) #NA
        with self.assertRaises(BirthdateOutOfRangeError):
            self.yourRANKToday(DoB=date(1920, 1, 1))
            # this would make the test pass! - self.yourRANKToday(DoB=date(1919, 12, 31))

    def test_yourRANKbyDate_atMinBirthdateAndAtMaxDate(self):   # hheimbuerger: a span of more than 36500 days was previously reported as an error -- if I remove that check for this
                                                                #               acceptance test, it turns out the algorithm can't actually handle those values and errors out internally now!
        # line 39: yourRANKbyDate(DoB,"2100/12/31") #349.4013
        self.assertAlmostEqual(self.yourRANKbyDate(DoB=date(1920, 1, 1), refdate=date(2100, 12, 31)), 349.4013, delta=5)

    def test_remle_atMinDate(self):
        # line 3: minimum Date to calcualte Life expectancy for the youngest
        # line 4: rem_le(CNTRY1="World",iSEX1 = 1,le_date=as.Date("1955-01-01"),le_exact_age=0)# $y = 58.1315 (remaining life expectancy)
        self.assertAlmostEqual(self.rem_le(le_date=date(1955, 1, 1), le_exact_age=relativedelta(years=0)), 58.1315, delta=1)

    def test_remle_atMaxDate(self):
        # line 6: maximum Date to calculate life expectancy for the oldest
        # line 7: rem_le(CNTRY1="World",iSEX1 = 1,le_date=as.Date("2124-12-31"),le_exact_age=130)# $y = 1.070459 (remaining life expectancy)
        self.assertAlmostEqual(self.rem_le(le_date=date(2124, 12, 31), le_exact_age=relativedelta(years=130)), 1.070459, delta=1)

    def test_remle_forNewborn(self):
        # line 9: maximum date to calculate life expectancy for a newborn
        # line 10: rem_le(CNTRY1="World",iSEX1 = 1,le_date=as.Date("2015-06-30"),le_exact_age=0) # $y = 75.60037
        self.assertAlmostEqual(self.rem_le(le_date=date(2015, 6, 30), le_exact_age=relativedelta(years=0)), 75.60037, delta=1)

    def test_remle_borderCase(self):
        # line 12: #this means at the moment,if the le_date and le_exact_age makes someone born after 2015-06-30,
        # line 13: #we should not be reporting life expectancy for the person
        # line 14: #Following is the border case...
        # line 15: le_date = as.Date("2015-07-01")
        # line 16: le_exact_age = 0
        # line 17: if(as.numeric(le_date) - le_exact_age*365 > as.numeric(as.Date(("2015-06-30")))) "You are too young"
        with self.assertRaises(EffectiveBirthdateOutOfRangeError):
            self.rem_le(le_date=date(2015, 7, 1), le_exact_age=relativedelta(years=0))
