
// mail problem by Tomas Holan

#include <boost/foreach.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/string/join.hpp>
#include <cmath>
#include <cassert>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <list>
#include <set>
#include <vector>

const int SIZE_X = 32;  
const int SIZE_Y = 32;  
const int CITIES_NUM = 1024;
const int TIME_ROUND_ONE_CENTER = 24/3 * 60;
const int TIME_ROUND_LOCAL_CENTERS = 24/4 * 60;
const int TIME_UNIT = 6; 
const int TIME_LOAD = 15; 

const char * ROUTES_FN = "routes.txt";
const char * WORLD_FN = "world.txt";

typedef int Distance;
typedef int City;
typedef int Time;
typedef std::list<City> Route;
typedef std::set<City> Cities;
typedef std::vector<City> CityList;
typedef std::vector<Route> Routes;
typedef Cities::const_iterator CitiesConstIt;

struct Center 
{
  City position; 
  Cities dependants; 

  Center(){};
  Center(City _city): 
    position(_city) {}
};

typedef std::vector<Center> CenterList;

// (row, col) counting from top left corner (0, 0) 
struct Coords
{
public:
  Coords(const int newRow, const int newCol): row(newRow), col(newCol){};
  Coords(const City& city ): row(city / SIZE_Y), col(city % SIZE_X){};
  int row;
  int col;
};

float sqr(float a) { return a * a;}
int flipCoin(float ratio) 
{
  return rand()/(RAND_MAX + 1.0) <= ratio;
} 
// evaluators
// Functors returning evaluation of the city (>0)
// evaluation == 0 => skip city (filter)
class CityEvaluator
{
public:
  CityEvaluator(){};
  static Distance calcPostDistance(const City& city1, const City& city2)
  {
    Coords coords1(city1);
    Coords coords2(city2);
    return abs(float(coords1.row - coords2.row)) + abs(float(coords1.col - coords2.col));
  } 
  static Distance calcEulerDistance(const City& city1, const City& city2)
  {
    Coords coords1(city1);
    Coords coords2(city2);
    return sqrt(sqr(abs(float(coords1.row - coords2.row))) + sqr(abs(float(coords1.col - coords2.col))));
  } 
};

// functor evaluating two cities as their distance
class CityDistanceEvaluator: public CityEvaluator
{
public:
  CityDistanceEvaluator(const City& baseCity, bool minimize, bool postDistance):
    mBaseCity(baseCity), 
    mMinimize(minimize), 
    mPostDistance(postDistance) {};
  float operator()(const City& city) {
    float distance = mPostDistance 
                     ? calcPostDistance(mBaseCity, city) 
                     : calcEulerDistance(mBaseCity, city);
    return  distance * (mMinimize ? -1 : 1);}
  float operator()(const Center& center) {
    float distance = mPostDistance
                     ? calcPostDistance(mBaseCity, center.position)
                     : calcEulerDistance(mBaseCity, center.position);
    return  distance * (mMinimize ? -1 : 1);}
private:
  City mBaseCity; 
  bool mMinimize;
  bool mPostDistance;
};

// functor evaluating how good is a city to become next in the route
class NextCityInRouteEvaluator: public CityEvaluator
{
public:
  NextCityInRouteEvaluator(const City& baseCity, const City& currentCity, const Time& remainingTime):
    mBaseCity(baseCity), mCurrentCity(currentCity), mRemainingTime(remainingTime) {};
  float operator()(const City& city) {
    Time necessaryTime = 
      TIME_UNIT * (calcPostDistance(mCurrentCity, city) + calcPostDistance(city, mBaseCity)) + TIME_LOAD;
    // no time to stop in this city
    if (mRemainingTime < necessaryTime)
    {
      return 0;
    }
    // the closer the city the better
    return - (calcPostDistance(mCurrentCity, city) 
              // locality element
              //+ flipCoin(0.25) * 0.01 * calcEulerDistance(city, mBaseCity)
              // random element
              //+ flipCoin(0.25) * 0.001
             );
  }
private:
  City mBaseCity; 
  City mCurrentCity;
  Time mRemainingTime;
};

// from given range gives element with best evaluation
template <typename Evaluator, typename ForwardIt> ForwardIt getBestEvalElem(ForwardIt begin, ForwardIt end, Evaluator evaluator)
{
  ForwardIt best = end;
  float bestEval;
  for (ForwardIt it = begin; it != end; it++)
  {
    float eval = evaluator(*it);
    if (eval && (best == end || bestEval < eval))
    {
      best = it;
      bestEval = eval;
    }
  }
  return best;
}

// create a route starting in given city
Route* planRoute(const City& baseCity, Cities& emptyCities, Time remainingTime)
{
  // select a city to start from - we take the closest one
  CitiesConstIt currentCityIt = emptyCities.begin(); 
    // minimize distance with post metric
    getBestEvalElem(emptyCities.begin(), emptyCities.end(), CityDistanceEvaluator(baseCity, true, true));
    // get random city 
    // std::advance(currentCityIt, rand() % emptyCities.size()); 
     
  assert(currentCityIt != emptyCities.end());
  //std::cout << "planning a route from " << *currentCityIt << endl;

  assert(remainingTime > 0);

  City lastCity = baseCity;
  Route* route = new Route();

  while (currentCityIt != emptyCities.end())
  {
    // bus goes to the current city and loads the mail
    remainingTime -= TIME_UNIT * CityEvaluator::calcPostDistance(lastCity, *currentCityIt) + TIME_LOAD;
    NextCityInRouteEvaluator evaluator(baseCity, *currentCityIt, remainingTime);
    lastCity = *currentCityIt;
    route->push_back(*currentCityIt);
    emptyCities.erase(*currentCityIt);
    // get best city we can reach in time
    currentCityIt = getBestEvalElem(emptyCities.begin(), emptyCities.end(), evaluator);
  }

  assert(route);
  return route;
}

std::string routeToStr(const Route& route)
{
  std::stringstream ss;
  ss.str("route: ");
  std::list<std::string> citiesNames;
  BOOST_FOREACH(City city, route)
  {
    citiesNames.push_back(boost::lexical_cast<std::string>(city));
  } 
  return boost::join(citiesNames, "->");
}

std::string citiesToStr(const Routes& routes)
{
  std::stringstream ss;
  // map cities to route lines
  int routeByCity[SIZE_X * SIZE_Y];
  for (int i=0; i < routes.size(); i++)
  {
    BOOST_FOREACH(City city, routes[i])
    {
      routeByCity[city] = i;
    }
  } 
  
  for (int i=0; i < SIZE_X * SIZE_Y; i++)
  {
    ss << std::setw(3) << routeByCity[i];
    if ((i + 1) % SIZE_X == 0)
    {
      ss << "\n";
    }
  }
  return ss.str();
} 

int main(int argc, char** argv)
{
  srand(unsigned(time(0)));
  // init structures
  bool useLocalCenters = false;
  if (argc >= 2 && strcmp(argv[1], "-l") == 0) 
    useLocalCenters = true; 

  // all the routes 
  Routes routes;
  Cities allCities;
  for (int i=0; i < SIZE_X * SIZE_Y; i++)
  {
    allCities.insert(i); 
  } 

  Center mainCenter(SIZE_X * SIZE_Y/2 + SIZE_X/2);
  CenterList centers;
  centers.push_back(mainCenter);

  if (useLocalCenters)
  {
    // at the moment 4 hardcoded local centers
    centers.push_back(Center(int(SIZE_X * SIZE_Y * 0.25 + SIZE_X * 0.25)));
    centers.push_back(Center(int(SIZE_X * SIZE_Y * 0.25 + SIZE_X * 0.75)));
    centers.push_back(Center(int(SIZE_X * SIZE_Y * 0.75 + SIZE_X * 0.25)));
    centers.push_back(Center(int(SIZE_X * SIZE_Y * 0.75 + SIZE_X * 0.75)));

    // centers are picked up implicitly
    BOOST_FOREACH(const Center& center, centers)
    {
      allCities.erase(center.position);
    }

    // split cities to local centers
    BOOST_FOREACH(const City& city, allCities)
    {
      CenterList::iterator it = 
        // minimize distance with euler metric
        getBestEvalElem(centers.begin(), centers.end(), CityDistanceEvaluator(city, true, false));
      it->dependants.insert(city);
    }
  }
  else
  {
    assert(centers.size() == 1);
    centers[0].dependants = allCities;
  }

  // generate routes
  for(CenterList::iterator it = centers.begin(); it != centers.end(); it++)
  {
    while (it->dependants.size() > 0)
    {
      Route* newRoute = planRoute(it->position, it->dependants, 
          useLocalCenters ? TIME_ROUND_LOCAL_CENTERS : TIME_ROUND_ONE_CENTER);
      routes.push_back(*newRoute);
    }
  }

  // print results
  std::fstream worldFile;
  worldFile.open(WORLD_FN, std::fstream::out);

  std::fstream routesFile;
  routesFile.open(ROUTES_FN, std::fstream::out);

  BOOST_FOREACH(const Center& center, centers)
  {
    routesFile << center.position << " ";
  }
  routesFile << std::endl;

  BOOST_FOREACH(const Route& route, routes)
  {
    std::cout << routeToStr(route) << std::endl;
    routesFile << routeToStr(route) << std::endl;
  } 
  std::cout << std::endl;
  std::cout << citiesToStr(routes) << std::endl;
  worldFile << citiesToStr(routes) << std::endl;
  std::cout << "Total " << routes.size() << " routes" << std::endl;
  std::cout << "Average Route Size: " << SIZE_X * SIZE_Y / float(routes.size()) << std::endl;
}

