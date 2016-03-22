#include <fstream>

void processfertility(const char* ifname="fertility.txt",const char* ofname="fertility.root"){

  vector<int> fage;
  vector<float> fpercent;

  //fage.push_back(0);
  //fpercent.push_back(0.0);

  ifstream marry(ifname);
  while(1){
    int year;
    float percent;
    marry >> year >> percent;
    if(!marry.good())break;
    fage.push_back(year);
    fpercent.push_back(percent);
  }

  TFile* outfile = new TFile(ofname,"RECREATE");

  TGraph* woman = new TGraph(fage.size());

  for(int i = 0; i < (int)fage.size(); i++){
    woman->SetPoint(i,fage[i],fpercent[i]);
  }

  woman->SetName("woman");
  woman->Write();
  outfile->Write();
  outfile->Close();

}
