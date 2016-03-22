#include "popsim.h"
using namespace std;

vector<Person*> men;
vector<Person*> women;
vector<Couple*> couples;
TH1F* nBabies;
TH1F* nSpouses;
TH1F* nBaby;
TH1F* nAge;

float mendeathprob[120];
float womendeathprob[120];

int main(int argc, char* argv[])
{
  int nYears = 1000;
  int targetPop = 2000;
  mCouples = 500;
  char ofname[100];
  sprintf(ofname,"popsim.root");

  int fm = 0;
  int fb = 0;

  if(argc > 1){
    int optind = 1;
    while(optind < argc){
      string sw = argv[optind];
      if(sw=="-t"){
        optind++;
        nYears = atoi(argv[optind]);
      }else if(sw=="-m"){
        optind++;
        mCouples = atoi(argv[optind]);
        targetPop = mCouples * 4;
      }else if(sw=="-o"){
        optind++;
        sprintf(ofname,"%s",argv[optind]);
      }else if(sw=="-fm"){
		fm = 1;
      }else if(sw=="-fb"){
		fb = 1;
      }else{
        cout<<"Unknown switch: "<<argv[optind]<<endl;
      }
      optind++;
    }
  }


  int id = init();
  srand(time(NULL));

  TFile outfile(ofname,"RECREATE");
  TH1F* age = new TH1F("age","Age",20,20,40);
  TH1F* tPop = new TH1F("tPop","Total Population",nYears,-0.5,nYears-0.5);
  TH1F* mPop = new TH1F("mPop","Male Population",nYears,-0.5,nYears-0.5);
  TH1F* fPop = new TH1F("fPop","Female Population",nYears,-0.5,nYears-0.5);
  TH1F* cPop = new TH1F("cPop","Couples Population",nYears,-0.5,nYears-0.5);
  nAge = new TH1F("nAge","nFemales at age",100,-0.5,99.5);
  nBaby = new TH1F("nBaby","nBabies at age",100,-0.5,99.5);
  nBabies = new TH1F("nBabies","Number of Babies",5,-0.5,4.5);
  nSpouses = new TH1F("nSpouses","Number of Spouses",5,-0.5,4.5);

  for(int year = 0; year < nYears; year++){
    int tot = 2*(int)couples.size()+(int)men.size()+(int)women.size();
    int nm = (int)men.size() + (int)couples.size();
    int nw = (int)women.size() + (int)couples.size();
    int nc = (int)couples.size();
    int sm = (int)men.size();
    int sw = (int)women.size();
    increaseage();
    int expectedDeath = (int)(0.5+guessdeath());
    //if(fb == 1)id = forcebabies(id);
    //else id = havebabies(id);
    int babyTarget = expectedDeath + max(targetPop-tot,targetPop-2*nm);
    id = smoothbabies(id,babyTarget);
    if(fm == 1)forcemarry();
    else marry();
    death();
    nm = (int)men.size() + (int)couples.size();
    nw = (int)women.size() + (int)couples.size();
    nc = (int)couples.size();
    sm = (int)men.size();
    sw = (int)women.size();
    tot = 2*(int)couples.size()+(int)men.size()+(int)women.size();
    tPop->Fill(year,tot);
    mPop->Fill(year,nm);
    fPop->Fill(year,nw);
    cPop->Fill(year,nc);
    if(tot > 0)cout<<year<<" "<<tot<<" "<<nm<<" "<<nw<<" "<<nc<<" "<<sm<<" "<<sw<<endl;
  }
  
  TH1F* fFert = (TH1F*)nBaby->Clone("fFert");
  fFert->Divide(nAge);

  outfile.Write();
  outfile.Close();

  return 0;
}

int init()
{

  ifstream deathprob("lifetable.txt");
  while(1){
    int age;
    string ml,wl;
    float mdp,wdp,mo,wo;
    deathprob>>age>>mdp>>ml>>mo>>wdp>>wl>>wo;
    if(!deathprob.good())break;
    mendeathprob[age] = mdp;
    womendeathprob[age] = wdp;
  }
  int id = 0;

  vector<int> p(2,-1);
  vector<int> gp(2,-1);
  vector<int> ggp(2,-1);
  vector<int> gggp(2,-1);

  TRandom3 randg(11234);

  for(unsigned int i = 0; i < mCouples; i++){
    Person* man = new Person(id,0,p,gp,ggp,gggp);
    id++;
    man->age = max((int)randg.Gaus(28.0,2.5),26);
    Person* woman = new Person(id,1,p,gp,ggp,gggp);
    id++;
    //men.push_back(man);
    //women.push_back(woman);
    woman->age = max((int)randg.Gaus(28.0,2.5),26);
    Couple* c = new Couple;
    c->man = man;
    c->woman = woman;
    c->man->spouse.push_back(c->woman->getId());
    c->woman->spouse.push_back(c->man->getId());
    couples.push_back(c);
  }

  return id;
}

void increaseage()
{
  for(unsigned int i = 0; i < men.size(); i++)men[i]->age++;
  for(unsigned int i = 0; i < women.size(); i++)women[i]->age++;
  for(unsigned int i = 0; i < couples.size(); i++){
    couples[i]->man->age++;
    couples[i]->woman->age++;
    couples[i]->nYears++;
  }
}

void forcemarry()
{
  vector<Person*> marrymen;
  vector<Person*> marrywomen;

  vector<int> menindex;
  vector<int> womenindex;

  vector<int> menremove;
  vector<int> womenremove;

  vector<int> mentaken;
  vector<int> womentaken;

  if(men.size() == 0)return;
  if(women.size() == 0) return;
  //cout<<"marrying "<<men.size()<<" men and "<<women.size()<<" women"<<endl;
  for(unsigned int i = 0; i < men.size(); i++){
    if(17 > men[i]->age)continue;
    if(men[i]->age > 45)continue;
    men[i]->status=1;
    marrymen.insert(marrymen.begin(),men[i]);
    menindex.insert(menindex.begin(),i);
    mentaken.insert(mentaken.begin(),0);
  }
  for(unsigned int i  = 0; i < women.size(); i++){
    if(17 > women[i]->age)continue;
    if(women[i]->age > 45)continue;
    women[i]->status=1;
    marrywomen.insert(marrywomen.begin(),women[i]);
    womenindex.insert(womenindex.begin(),i);
    womentaken.insert(womentaken.begin(),0);
  }
  cout<<"found "<<marrymen.size()<<" men and "<<marrywomen.size()<<endl;
  for(unsigned int i = 0; i < marrymen.size(); i++){
    for(unsigned int j = 0; j < marrywomen.size(); j++){
      if(womentaken[j])continue;
      //cout<<marrymen[i]->getId()<<" "<<marrywomen[j]->getId()<<" "<<marrymen[i]->canMarry(marrywomen[j])<<endl;
      if(marrymen[i]->canMarry(marrywomen[j])){
		//cout<<i<<" and "<<j<<" are getting married"<<endl;
		Couple* c = new Couple;
		c->man = new Person(marrymen[i]);
		c->woman = new Person(marrywomen[j]);
		c->man->spouse.push_back(c->woman->getId());
		c->woman->spouse.push_back(c->man->getId());
		marrymen[i]->status=0;
		marrywomen[j]->status=0;
		couples.push_back(c);
		menremove.push_back(menindex[i]);
		womenremove.push_back(womenindex[j]);
		womentaken[j] = 1;
		//womenindex.erase(womenindex.begin() + j);
		//marrywomen.erase(marrywomen.begin() + j);
		break;
      }
    }
  }
  //cout<<"married "<<menremove.size()<<" men and "<<womenremove.size()<<" women, out of "<<marrymen.size()<<" and "<<marrywomen.size()<<endl;
  sort(menremove.begin(),menremove.end());
  sort(womenremove.begin(),womenremove.end());
  for(unsigned int i = menremove.size(); i > 0; i--){
    men.erase(men.begin() + menremove[i-1]);
  }
  for(unsigned int i = womenremove.size(); i > 0; i--){
    women.erase(women.begin() + womenremove[i-1]);
  }
  

}

void marry()
{
  vector<Person*> marrymen;
  vector<Person*> marrywomen;

  vector<int> menindex;
  vector<int> womenindex;

  vector<int> menremove;
  vector<int> womenremove;

  vector<int> mentaken;
  vector<int> womentaken;

  if(men.size() == 0)return;
  if(women.size() == 0) return;
  //cout<<"marrying "<<men.size()<<" men and "<<women.size()<<" women"<<endl;
  for(unsigned int i = 0; i < men.size(); i++){
    float r = (float)rand()/RAND_MAX;
    if(men[i]->status == 1){
      marrymen.push_back(men[i]);
      menindex.push_back(i);
      mentaken.push_back(0);
      continue;
    }
    if(r > manmarry(men[i]->age))continue;
    men[i]->status=1;
    marrymen.push_back(men[i]);
    menindex.push_back(i);
    mentaken.push_back(0);
  }
  for(unsigned int i  = 0; i < women.size(); i++){
    float r = (float)rand()/RAND_MAX;
    if(women[i]->status==1){
      marrywomen.push_back(women[i]);
      womenindex.push_back(i);
      womentaken.push_back(0);
      continue;
    }
    if(r > womanmarry(women[i]->age))continue;
    women[i]->status=1;
    marrywomen.push_back(women[i]);
    womenindex.push_back(i);
    womentaken.push_back(0);
  }
  //cout<<"found "<<marrymen.size()<<" men and "<<marrywomen.size()<<endl;
  for(unsigned int i = 0; i < marrymen.size(); i++){
    for(unsigned int j = 0; j < marrywomen.size(); j++){
      if(womentaken[j])continue;
      if(marrymen[i]->canMarry(marrywomen[j])){
	//cout<<i<<" and "<<j<<" are getting married"<<endl;
	Couple* c = new Couple;
	c->man = new Person(marrymen[i]);
	c->woman = new Person(marrywomen[j]);
	c->man->spouse.push_back(c->woman->getId());
	c->woman->spouse.push_back(c->man->getId());
	marrymen[i]->status=0;
	marrywomen[j]->status=0;
	couples.push_back(c);
	menremove.push_back(menindex[i]);
	womenremove.push_back(womenindex[j]);
	womentaken[j] = 1;
	//womenindex.erase(womenindex.begin() + j);
	//marrywomen.erase(marrywomen.begin() + j);
	break;
      }
    }
  }
  //cout<<"married "<<menremove.size()<<" men and "<<womenremove.size()<<" women"<<endl;
  sort(menremove.begin(),menremove.end());
  sort(womenremove.begin(),womenremove.end());
  for(unsigned int i = menremove.size(); i > 0; i--){
    men.erase(men.begin() + menremove[i-1]);
  }
  for(unsigned int i = womenremove.size(); i > 0; i--){
    women.erase(women.begin() + womenremove[i-1]);
  }

}

float guessdeath()
{
  float tot = 0;
  if(men.size() > 0){
    for(unsigned int i = men.size(); i > 0; i--){
      float d = mendeathprob[119];
      if(men[i-1]->age < 120)d = mendeathprob[men[i-1]->age];
      tot += d;
    }
  }
  if(women.size() > 0){
    for(unsigned int i = women.size(); i > 0; i--){
      float d = womendeathprob[119];
      if(women[i-1]->age < 120)d = womendeathprob[women[i-1]->age];
      tot += d;
    }
  }
  if(couples.size() > 0){
    for(unsigned int i = couples.size(); i > 0; i--){
      float dw = womendeathprob[119];
      float dm = mendeathprob[119];
      if(couples[i-1]->woman->age < 120)dw = womendeathprob[couples[i-1]->woman->age];
      if(couples[i-1]->man->age < 120)dm = mendeathprob[couples[i-1]->man->age];
      tot += dw + dm;
    }
  }
  
  return tot;
}


void death()
{
  if(men.size() > 0){
    for(unsigned int i = men.size(); i > 0; i--){
      float r = (float)rand()/RAND_MAX;
      float d = mendeathprob[119];
      if(men[i-1]->age < 120)d = mendeathprob[men[i-1]->age];
      if(r > d)continue;
      //Person* m = men[i-1];
      men.erase(men.begin()+i-1);
      //delete m;
    }
  }
  if(women.size() > 0){
    for(unsigned int i = women.size(); i > 0; i--){
      float r = (float)rand()/RAND_MAX;
      float d = womendeathprob[119];
      if(women[i-1]->age < 120)d = womendeathprob[women[i-1]->age];
      if(r > d)continue;
      //Person* w = women[i-1];
      if(women[i-1]->getId() >= 0){
	    nBabies->Fill(women[i-1]->children.size());
	    nSpouses->Fill(women[i-1]->spouse.size());
      }
      women.erase(women.begin()+i-1);
      //delete w;
    }
  }
  if(couples.size() > 0){
    for(unsigned int i = couples.size(); i > 0; i--){
      float rw = (float)rand()/RAND_MAX;
      float dw = womendeathprob[119];
      float rm = (float)rand()/RAND_MAX;
      float dm = mendeathprob[119];
      if(couples[i-1]->woman->age < 120)dw = womendeathprob[couples[i-1]->woman->age];
      if(couples[i-1]->man->age < 120)dm = mendeathprob[couples[i-1]->man->age];
      if(rm > dm && rw > dw)continue;
      Person* w = new Person(couples[i-1]->woman);
      Person* m = new Person(couples[i-1]->man);
      //Couple* c = couples[i-1];
      couples.erase(couples.begin()+i-1);
      //delete c;
      if(rm < dm){
		delete m;
      }else{
		vector<Person*>::iterator iTer;
		for(iTer = men.begin(); iTer != men.end(); iTer++){
			if((*iTer)->age < m->age){
				men.insert(iTer,m);
				break;
			}
		}
		if(iTer == men.end())men.push_back(m);
      }
      if(rw < dw){
		if(w->getId() >= 0){
	  		nBabies->Fill(w->children.size());
			nSpouses->Fill(w->spouse.size());
		}
		delete w;
      }else{
		vector<Person*>::iterator iTer;
		for(iTer = women.begin(); iTer != women.end(); iTer++){
			if((*iTer)->age < w->age){
				women.insert(iTer,w);
				break;
			}
		}
		if(iTer == women.end())women.push_back(w);
      }
    }
  }
}

int havebabies(int id)
{
  //cout<<"baby loop"<<endl;
  for(unsigned int i = 0; i < couples.size(); i++){
    if(couples[i]->woman->children.size() >= 2)continue;
    float r = (float)rand()/RAND_MAX;
    float f = fertile(couples[i]->woman->age);
    nAge->Fill(couples[i]->woman->age);
    //cout<<couples[i]->woman->getId()<<" "<<couples[i]->woman->children.size()<<" "<<f<<" "<<r<<endl;
    if(r > f)continue;
    nBaby->Fill(couples[i]->woman->age);
    int s = (int)floor(0.5+(float)rand()/RAND_MAX);
    vector<int> parents;
    parents.push_back(couples[i]->woman->getId());
    parents.push_back(couples[i]->man->getId());
    Person* baby = new Person(id,s,couples[i]->getParents(),couples[i]->getGrandparents(),couples[i]->getGreatgrandparents(),couples[i]->getGreatgreatgrandparents());
    couples[i]->woman->children.push_back(id);
    couples[i]->man->children.push_back(id);
    id++;
    //cout<<"new baby "<<id<<" "<<s<<endl;
    if(s == 0)men.push_back(baby);
    if(s == 1)women.push_back(baby);
  }
  return id;
}

void printAncestors(Person* baby)
{
	cout<<baby->getId()<<" ";
	for(unsigned int i = 0; i < baby->parents.size(); i++){
		cout<<baby->parents.at(i)<<" ";
	}
	for(unsigned int i = 0; i < baby->grandparents.size(); i++){
		cout<<baby->grandparents.at(i)<<" ";
	}
	for(unsigned int i = 0; i < baby->greatgrandparents.size(); i++){
		cout<<baby->greatgrandparents.at(i)<<" ";
	}
	for(unsigned int i = 0; i < baby->greatgreatgrandparents.size(); i++){
		cout<<baby->greatgreatgrandparents.at(i)<<" ";
	}
	cout<<endl;
}

int forcebabies(int id)
{
  for(unsigned int i = 0; i < couples.size(); i++){
    if(couples[i]->woman->children.size() >= 2)continue;
    //if(couples[i]->woman->age != 25 && couples[i]->woman->age != 30)continue;
    int s = (int)floor(0.5+(float)rand()/RAND_MAX);
    vector<int> parents;
    parents.push_back(couples[i]->woman->getId());
    parents.push_back(couples[i]->man->getId());
    Person* baby = new Person(id,s,couples[i]->getParents(),couples[i]->getGrandparents(),couples[i]->getGreatgrandparents(),couples[i]->getGreatgreatgrandparents());
    couples[i]->woman->children.push_back(id);
    couples[i]->man->children.push_back(id);
    id++;
    //cout<<"new baby "<<id<<" "<<s<<endl;
    if(s == 0)men.push_back(baby);
    if(s == 1)women.push_back(baby);
  }
  return id;
}

int smoothbabies(int id, int target)
{
  int total = 0;
  vector<vector<Couple*> > couplesByChildren;
  for(unsigned int i = 0; i < 5; i++){
  	vector<Couple*> c;
  	couplesByChildren.push_back(c);
  }
  for(unsigned int i = 0; i < couples.size(); i++){
  	int nChildren = couples[i]->woman->children.size();
  	if(nChildren > couplesByChildren.size())continue;
  	vector<Couple*>::iterator iTer;
  	for(iTer = couplesByChildren[nChildren].begin(); iTer != couplesByChildren[nChildren].end(); iTer++){
  		if((*iTer)->woman->age > couples[i]->woman->age){
  			couplesByChildren[nChildren].insert(iTer,couples[i]);
  			break;
  		}
  	}
  	if(iTer == couplesByChildren[nChildren].end()){
  		couplesByChildren[nChildren].push_back(couples[i]);
  	}
  }
  for(unsigned int i = 0; i < 5; i++){
	if (total >= target)break;
  	for(unsigned int j = 0; j < couplesByChildren[i].size(); j++){
		if (total >= target)break;
	    int s = (int)floor(0.5+(float)rand()/RAND_MAX);
	    //cout<<i<<" "<<j<<" "<<couplesByChildren[i][j]->woman->getId()<<" "<<couplesByChildren[i][j]->man->getId()<<endl;
    	vector<int> parents;
	    parents.push_back(couplesByChildren[i][j]->woman->getId());
    	parents.push_back(couplesByChildren[i][j]->man->getId());
	    Person* baby = new Person(id,s,couplesByChildren[i][j]->getParents(),couplesByChildren[i][j]->getGrandparents(),couplesByChildren[i][j]->getGreatgrandparents(),couplesByChildren[i][j]->getGreatgreatgrandparents());
    	couplesByChildren[i][j]->woman->children.push_back(id);
	    couplesByChildren[i][j]->man->children.push_back(id);
    	id++;
    	total++;
	    //printAncestors(baby);
	    if(s == 0)men.push_back(baby);
    	if(s == 1)women.push_back(baby);
  	}
  }
  return id;
}


float manmarry(float t)
{
  float a = 0.98;
  float b = 5263;
  float c = 0.3796;

  return a*b*c*exp(-c*t)/pow(1+b*exp(-c*t),2);
}
float womanmarry(float t)
{
  float a = 0.98;
  float b = 398;
  float c = 0.3137;

  return a*b*c*exp(-c*t)/pow(1+b*exp(-c*t),2);
}

float fertile(float t)
{
  if(t < 17)return 0;
  if(t > 45)return 0;
  float f = 581.8 + -159*t + 15.16*pow(t,2) - 0.607*pow(t,3) + 0.0108*pow(t,4) - 7.095e-5*pow(t,5);
  float k = 2.0;
  //float k = 1.43;
  //float a0 = 581.8;
  //float a1 = -159.0;
  //float a2 = 15.16;
  //float a3 = -0.607;
  //float a4 = 0.0108;
  //float a5 = -7.095e-5;
  //float f = pow(t,5)*a5 + pow(t,4)*(a4 + a5*5./2.) + pow(t,3)*(a3 + 2.*a4 + a5*10./3.) + pow(t,2) * (a2 + a3*3./2. + a4*2. + a5*5./2.) + t * (a1 + a2 + a3 + a4 + a5) + (a0 + a1/2. + a2/3. + a3/4. + a4/5. + a5/6.);
  //printf("%2.2f %2.2f\n",f0,f);

  return f/1000;

}
