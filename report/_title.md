---
geometry: margin=2.2cm
fontsize: 11pt
linkcolor: blue
urlcolor: blue
colorlinks: true
mainfont: "Arial Unicode MS"
monofont: "Menlo"
header-includes:
    - \usepackage{newunicodechar}
    - \newunicodechar{⋃}{\ensuremath{\bigcup}}
    - \usepackage{fancyhdr}
    - \pagestyle{fancy}
    - \fancyhf{}
    - \fancyfoot[C]{\thepage}
    - \fancyhead[L]{Disease Outbreak --- Take-home Assignment}
    - \fancyhead[R]{COSC2123/3119}
    - \renewcommand{\headrulewidth}{0.4pt}
---

\thispagestyle{empty}

\vspace*{3cm}

\begin{center}
{\Huge\bfseries Graph Algorithms in Action}\\[0.4cm]
{\LARGE Modelling a Disease Outbreak}\\[1.5cm]
{\Large Take-Home Assignment Report}\\[0.6cm]
{\large COSC2123/3119 --- Algorithms and Analysis}\\[0.3cm]
{\large RMIT University --- Semester 1, 2026}
\end{center}

\vspace{3cm}

\begin{center}
\begin{tabular}{ll}
\textbf{Section} & \textbf{Marks} \\
\hline
Task B --- Infection Risk DP & 4 \\
Task C --- Empirical Analysis & 8 \\
Task D --- Antiviral Allocation & 6 \\
\hline
\textbf{Total} & \textbf{18} \\
\end{tabular}
\end{center}

\vfill

\begin{center}
\small\emph{Task A (adjacency matrix implementation) is code-only and carries\\no report marks per the assignment specification.}
\end{center}

\newpage
