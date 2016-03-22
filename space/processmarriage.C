#include <fstream>

void processmarriage(const char* ifname="marry.txt",const char* ofname="marry.root"){

  vector<int> mage;
  vector<float> mpercent;

  vector<int> fage;
  vector<float> fpercent;

  mage.push_back(0);
  mpercent.push_back(0.0);
  fage.push_back(0);
  fpercent.push_back(0.0);

  ifstream marry(ifname);
  while(1){
    int gender,year;
    float percent;
    marry >> gender >> year >> percent;
    if(!marry.good())break;
    if(gender == 1){
      mage.push_back(year);
      mpercent.push_back(percent);
    }
    if(gender == 0){
      fage.push_back(year);
      fpercent.push_back(percent);
    }
  }

  TFile* outfile = new TFile(ofname,"RECREATE");

  TGraph* man = new TGraph(mage.size());
  TGraph* woman = new TGraph(fage.size());

  for(int i = 0; i < (int)mage.size(); i++){
    man->SetPoint(i,mage[i],mpercent[i]);
  }
  for(int i = 0; i < (int)fage.size(); i++){
    woman->SetPoint(i,fage[i],fpercent[i]);
  }

  man->SetName("man");
  woman->SetName("woman");
  man->Write();
  woman->Write();
  outfile->Write();
  outfile->Close();

}
