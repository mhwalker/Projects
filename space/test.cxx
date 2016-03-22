#include "test.h"
#include "TRandom3.h"
#include "TH1.h"
#include "TFile.h"
using namespace std;

int main(void)
{
  vector<Person*> men;
  vector<Person*> women;
  vector<Couple*> couples;

  int id = 0;
  vector<int> p;
  vector<int> gp;
  vector<int> ggp;
  vector<int> gggp;

  TRandom3 randg(11234);
  TFile outfile("test.root","RECREATE");
  TH1F* age = new TH1F("age","Age",20,20,40);

  for(unsigned int i = 0; i < 500; i++){
    Person* man = new Person(id,0,p,gp,ggp,gggp);
    id++;
    man->age = max((int)randg.Gaus(32.0,2.5),26);
    Person* woman = new Person(id,1,p,gp,ggp,gggp);
    id++;
    woman->age = max((int)randg.Gaus(32.0,2.5),26);
    Couple* c = new Couple;
    c->man = man;
    c->woman = woman;
    age->Fill(man->age);
    age->Fill(woman->age);
  }

  outfile.Write();
  outfile.Close();

  return 0;
}

