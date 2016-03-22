#include <vector>
#include <algorithm>
#include <iostream>

class Person
{
 private:
  int id;
 public:
  Person(int,int,std::vector<int>,std::vector<int>,std::vector<int>,std::vector<int>);
  Person(Person*);
  ~Person();

  int getId() {return id;}
  int age;
  int status;
  std::vector<int> parents;
  std::vector<int> grandparents;
  std::vector<int> greatgrandparents;
  std::vector<int> greatgreatgrandparents;
  int gender;
  std::vector<int> children;
  std::vector<int> spouse;

  bool canMarry(Person*);
};

class Couple
{
 public:
  Couple();
  ~Couple();

  Person* man;
  Person* woman;

  int nYears;

  std::vector<int> getParents();
  std::vector<int> getGrandparents();
  std::vector<int> getGreatgrandparents();
  std::vector<int> getGreatgreatgrandparents();
};
