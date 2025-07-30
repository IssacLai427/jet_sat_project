import ROOT
import numpy as np
import os
import shutil
import argparse
np.set_printoptions(suppress=True)

parser = argparse.ArgumentParser()
parser.add_argument('channel', choices=["LO", "NLO", "NNLO"], help='Channel to process')
parser.add_argument('pdf', choices=["CT18", "MSHT20", "NNPDF40"], help='PDF to process')
parser.add_argument('policy', choices=["local", "htcondor"], help='submission policy')
args = parser.parse_args()

channel = args.channel
pdf = args.pdf
policy = args.policy

#channel = input("Channel(LO,NLO,NNLO)")
#pdf = input("pdf(CT18,MSHT20,NNPDF40)")
#movefile = input("move the newly-transfered outputs? (y/n)")

ch = channel.lower()
sqrts = [1,3,7,20,50,100,300,1000]
pTmin = [1,2,5,10,20,35]
start_dir = os.getcwd()
os.chdir(f"output/{channel}/{pdf}")


if policy == "local":
    for s in sqrts:
        try:
            shutil.move(f"result_sqrts={s}TeV", f"sqrts={s}TeV_{channel}_{pdf}/result")
            #shutil.move(f"raw_sqrts={s}TeV", f"sqrts={s}TeV_{channel}_{pdf}/raw")
        except:
            break

for s in sqrts:
    # Step 1: Change to the target directory
    os.chdir(f"sqrts={s}TeV_{channel}_{pdf}")
    pT = []
    xmin = []
    x = []
    xmax = []

    for p in pTmin:
        file=open(f"result/final/{ch}.cross_{p}GeV.dat")
        A=np.genfromtxt(file,skip_header=2)
        B=[A[2*k] for k in range(0,7)]
        pT.append(p)
        xmin.append(min(B))
        x.append(B[0])
        xmax.append(max(B))

    d = np.array([pT,xmin,x,xmax])
    D = np.column_stack((d))
    hdr="pT_min , x_min , x , x_max"
    np.savetxt(f'{s}TeV_result.dat', D, fmt="%30.5f", header = hdr)
    os.chdir("..")

n=6
pTmin = np.array([float(p) for p in pTmin])
ss = np.array([float(s) for s in sqrts])

def data(s):
    file=open(f"sqrts={s}TeV_{channel}_{pdf}/{s}TeV_result.dat")
    A=np.genfromtxt(file,skip_header=1)
    pT,xmin,x,xmax=np.column_stack(A)
    dxp = xmax-x
    dxm = x-xmin
    xmax = xmax*1E-12
    dxp = dxp*1E-12
    x = x*1E-12
    dxm = dxm*1E-12
    xmin = xmin*1E-12
    return x, dxm, dxp, xmin, xmax

def plot(s,k):
    # Create a TGraph object using the defined X and Y values
    curve = ROOT.TGraphAsymmErrors(n, pTmin, data(s)[0], 0, 0, data(s)[1], data(s)[2])
    # Customize graph appearance
    curve.SetTitle(f"{s}TeV")
    if k < 6:
        curve.SetMarkerStyle(20)
    else:
        curve.SetMarkerStyle(22)
    curve.SetMarkerSize(1)
    curve.SetMarkerColor(k+2)
    curve.SetLineColor(0)
    curve.SetLineStyle(1)
    curve.SetLineWidth(1)
    return curve

# Create a canvas to draw the graph
canvas = ROOT.TCanvas("c1", "TGraph Example", 1600, 1200)
canvas.SetLogx()
canvas.SetLogy()

graph = ROOT.TMultiGraph()
fit = ROOT.TF1("fit","[1]*([0]/x)^(1/[2])-[1]",1,40)
fit.SetParameters(1E6,2,2)

X_NN = ROOT.TF1("X_NN","[0]+[1]*pow(log(pow(1000*x,2)),[2])",1,1000)
X_NN.SetParameters(28.84,0.0458,2.374)
Py = []
Px = []

for k,s in enumerate(sqrts):
    curve = plot(s,k)
    fit.SetLineColor(k+2)
    curve.Fit("fit","","R",1, 40)
    graph.Add(curve)
    x_NN = X_NN.Eval(s)
    Py.append(x_NN)
    Px.append(fit.GetX(x_NN))

Px = np.array(Px)
Py = np.array(Py)
x_inel = ROOT.TGraph(8,Px,Py)
x_inel.SetTitle(fr"\sigma_{{NN}}")
x_inel.SetMarkerStyle(21)
x_inel.SetMarkerSize(1)
x_inel.SetMarkerColor(1)
x_inel.SetLineColor(1)
x_inel.SetLineStyle(1)
x_inel.SetLineWidth(1)
graph.Add(x_inel)

graph.SetTitle(fr"\sigma_{{jet}} vs p_{{T min}} at {channel}, pdf={pdf}")
graph.GetYaxis().SetTitle(r"\sigma [mb]")
graph.GetXaxis().SetTitle("p_{T min} [GeV]")
graph.GetXaxis().SetLimits(0.9,40)
graph.SetMinimum(1e-5)
graph.SetMaximum(1e5)

graph.Draw("ALP")
canvas.BuildLegend()

# Save the graph as a PNG file
canvas.SaveAs(f"{channel}_{pdf}.png")

os.chdir(f"{start_dir}/output")

def remove_graph_by_title(mg, title):
    graphs = mg.GetListOfGraphs()
    if not graphs:
        # Nothing to do, no graphs in the multigraph
        return 0
    to_remove = []
    for i in range(graphs.GetSize()):
        g = graphs.At(i)
        if g and g.GetTitle() == title:
            to_remove.append(g)
    for g in to_remove:
        graphs.Remove(g)
    return graphs.GetSize()

with ROOT.TFile("jet_saturation.root", "UPDATE") as r:
    graph.Write(f"{channel}_{pdf}", ROOT.TFile.kOverwrite)
    mg = r.Get("All_pltex")
    if not mg:
        mg = ROOT.TMultiGraph("All_pltex", "All pltex graphs")
    
    pltex = ROOT.TGraph(8,ss,Px)
    pltex.SetTitle(f"{channel}_{pdf}")
    cln = remove_graph_by_title(mg, pltex.GetTitle())
    
    fit2 = ROOT.TF1("fit2","[0]*pow(x, [1])",1,1000)
    fit2.SetLineColor(cln+2)
    pltex.Fit("fit2","","R",1, 1000)
    
    pltex.SetMarkerStyle(21)
    pltex.SetMarkerSize(1)
    pltex.SetMarkerColor(cln+2)
    pltex.SetLineColor(0)
    pltex.SetLineStyle(1)
    pltex.SetLineWidth(1)
    mg.Add(pltex)

    mg.SetTitle(r"p_{{T min}} at \sigma_{{NN}} vs \sqrt{s} for different channels and pdf")
    mg.GetYaxis().SetTitle(r"p_{T min} [GeV]")
    mg.GetXaxis().SetTitle(r"\sqrt{s} [TeV]")
    mg.GetXaxis().SetLimits(0.9,1500)
    mg.SetMinimum(0.9)
    mg.SetMaximum(50)

    mg.Write("All_pltex", ROOT.TObject.kOverwrite)
    r.Close()

canvas2 = ROOT.TCanvas("c2", "TGraph Example2", 1600, 1200)
canvas2.SetLogx()
canvas2.SetLogy()
mg.Draw("ALP")
canvas2.BuildLegend()

canvas2.SaveAs("x_NN.png")