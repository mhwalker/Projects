cd ~/projects/eveOnline/algoTrading/
python getCurrentPrices.py 
python makePage.py
if [ -e index.html ]
then
    rm index.html
fi
cat head.html body.html foot.html > index.html
cp index.html /data/www/analysis
python makePageNewbro.py
if [ -e index_newbro.html ]
then 
    rm index_newbro.html
fi
cat head.html body_newbro.html foot.html > index_newbro.html
cp index_newbro.html /data/www/trading/index.html