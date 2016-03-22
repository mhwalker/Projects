#include <fstream>

void drawFrequency(const char* ifname="output/HUMAN.pair.output", int type=2)
{
	gROOT->SetStyle("Plain");
	
	TFile outfile(TString(TString(ifname)+".root"),"RECREATE");
	int nbins = 400;
	if(type == 1)nbins = 20;
	TH1F* freq = new TH1F("freq","",nbins,-0.5,float(nbins)-0.5);
	
	int bin = 1;
	ifstream infile(ifname);
	while(1){
		TString name;
		float freq1,freq2;
		infile >> name >> freq1;
		if(type == 2) infile >> freq2;
		if(!infile.good()) break;
		freq->SetBinContent(bin,freq1);
		bin++;
	}
	infile.close();
	
	TCanvas* c = new TCanvas("c","",800,600);
	gStyle->SetOptStat(0);
	freq->SetYTitle("Frequency");
	freq->SetXTitle("Amino acid pair");
	if(type == 1)freq->SetXTitle("Amino acid");
	freq->SetLineWidth(2);
	freq->SetLineColor(kBlue);
	freq->Draw();
	c->SaveAs(TString(TString(ifname)+".pdf"));
	outfile.Close();
}