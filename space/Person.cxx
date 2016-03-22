#include "Person.h"
using namespace std;

Person::Person(int id,int sex,vector<int>p,vector<int>gp,vector<int>ggp,vector<int>gggp):id(id),status(0),age(0),gender(sex),parents(p),grandparents(gp),greatgrandparents(ggp),greatgreatgrandparents(gggp)
{

}
Person::Person(Person* person)
{
  id = person->getId();
  age = person->age;
  status = person->status;
  parents = person->parents;
  grandparents = person->grandparents;
  greatgrandparents = person->greatgrandparents;
  greatgreatgrandparents = person->greatgreatgrandparents;
  gender = person->gender;
  children = person->children;
  spouse = person->spouse;
}
Person::~Person()
{
  parents.clear();
  grandparents.clear();
  greatgrandparents.clear();
  greatgreatgrandparents.clear();
  spouse.clear();
  children.clear();
}
bool Person::canMarry(Person* sp)
{
  vector<int> a;
  vector<int>::iterator ia = a.begin();
  vector<int> b;
  vector<int>::iterator ib = b.begin();

  //cout<<id<<" "<<sp->getId()<<endl;

  if(greatgreatgrandparents.size() > 0)a.insert(ia,greatgreatgrandparents.begin(),greatgreatgrandparents.end());
  ia = a.begin();
  if(greatgrandparents.size() > 0)a.insert(ia,greatgrandparents.begin(),greatgrandparents.end());
  ia = a.begin();
  if(grandparents.size() > 0)a.insert(ia,grandparents.begin(),grandparents.end());
  ia = a.begin();
  if(parents.size() > 0)a.insert(ia,parents.begin(),parents.end());
  ia = a.begin();
  a.push_back(id);

  if(sp->greatgreatgrandparents.size() > 0)b.insert(ib,sp->greatgreatgrandparents.begin(),sp->greatgreatgrandparents.end());
  ib = b.begin();
  if(sp->greatgrandparents.size() > 0)b.insert(ib,sp->greatgrandparents.begin(),sp->greatgrandparents.end());
  ib = b.begin();
  if(sp->grandparents.size() > 0)b.insert(ib,sp->grandparents.begin(),sp->grandparents.end());
  ib = b.begin();
  if(sp->parents.size() > 0)b.insert(ib,sp->parents.begin(),sp->parents.end());
  ib = b.begin();
  b.push_back(sp->getId());
  //cout<<a.size()<<" "<<b.size()<<endl;
  for(ia = a.begin(); ia != a.end(); ++ia){
  	if((*ia) < 0) continue;
    ib = find(b.begin(),b.end(),*ia);
    //cout<<(*ia)<<" "<<(*ib)<<endl;
    if(ib != b.end())return false;
  }
  return true;
}

Couple::Couple():nYears(0)
{
  man = 0;
  woman = 0;
}
Couple::~Couple()
{

}
vector<int> Couple::getParents()
{
  vector<int> a;
  a.push_back(man->getId());
  a.push_back(woman->getId());

  return a;
}
vector<int> Couple::getGrandparents()
{
  vector<int> a;
  vector<int>::iterator ia;
  ia = a.begin();
  if(man->parents.size() > 0)a.insert(ia,man->parents.begin(),man->parents.end());
  ia = a.begin();
  if(woman->parents.size() > 0)a.insert(ia,woman->parents.begin(),woman->parents.end());

  return a;
}
vector<int> Couple::getGreatgrandparents()
{
  vector<int> a;
  vector<int>::iterator ia;
  ia = a.begin();
  if(man->grandparents.size() > 0)a.insert(ia,man->grandparents.begin(),man->grandparents.end());
  ia = a.begin();
  if(woman->grandparents.size() > 0)a.insert(ia,woman->grandparents.begin(),woman->grandparents.end());

  return a;
}
vector<int> Couple::getGreatgreatgrandparents()
{
  vector<int> a;
  vector<int>::iterator ia;
  ia = a.begin();
  if(man->greatgrandparents.size() > 0)a.insert(ia,man->greatgrandparents.begin(),man->greatgrandparents.end());
  ia = a.begin();
  if(woman->greatgrandparents.size() > 0)a.insert(ia,woman->greatgrandparents.begin(),woman->greatgrandparents.end());

  return a;
}
