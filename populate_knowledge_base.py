from pathlib import Path

KB = Path("knowledge_base")
KB.mkdir(exist_ok=True)

files = {}

files["algebra.txt"] = """ALGEBRA FORMULAS AND IDENTITIES

1. QUADRATIC FORMULA
For ax^2 + bx + c = 0:
x = (-b +/- sqrt(b^2 - 4ac)) / 2a
Discriminant D = b^2 - 4ac
- D > 0: two distinct real roots
- D = 0: one repeated real root
- D < 0: two complex conjugate roots

Vieta's formulas: sum of roots = -b/a, product of roots = c/a

2. ALGEBRAIC IDENTITIES
(a+b)^2 = a^2 + 2ab + b^2
(a-b)^2 = a^2 - 2ab + b^2
(a+b)(a-b) = a^2 - b^2
(a+b)^3 = a^3 + 3a^2b + 3ab^2 + b^3
(a-b)^3 = a^3 - 3a^2b + 3ab^2 - b^3
a^3 + b^3 = (a+b)(a^2 - ab + b^2)
a^3 - b^3 = (a-b)(a^2 + ab + b^2)

3. ARITHMETIC PROGRESSION (AP)
nth term: a_n = a + (n-1)d
Sum of n terms: S_n = n/2 * (2a + (n-1)d) = n/2 * (a + l)
where a = first term, d = common difference, l = last term

4. GEOMETRIC PROGRESSION (GP)
nth term: a_n = a * r^(n-1)
Sum of n terms: S_n = a(r^n - 1)/(r - 1) for r != 1
Sum to infinity: S_inf = a/(1-r) for |r| < 1

5. INEQUALITIES
AM >= GM: (a+b)/2 >= sqrt(ab) for a,b > 0
AM-GM-HM inequality: AM >= GM >= HM

6. LOGARITHMS
log_a(xy) = log_a(x) + log_a(y)
log_a(x/y) = log_a(x) - log_a(y)
log_a(x^n) = n * log_a(x)
Change of base: log_a(x) = log_b(x) / log_b(a)
log_a(1) = 0, log_a(a) = 1

7. BINOMIAL THEOREM
(a+b)^n = sum_{k=0}^{n} C(n,k) * a^(n-k) * b^k
C(n,k) = n! / (k! * (n-k)!)
General term: T_{r+1} = C(n,r) * a^(n-r) * b^r
Middle term: if n even, middle term is T_{n/2+1}

8. COMPLEX NUMBERS
i^2 = -1, i^3 = -i, i^4 = 1
|z| = sqrt(a^2 + b^2) for z = a + ib
Conjugate: z* = a - ib
z * z* = |z|^2

COMMON MISTAKES IN ALGEBRA
- Forgetting +/- when taking square roots
- Sign errors when expanding (a-b)^2
- Division by zero when simplifying expressions
- Not checking if discriminant conditions hold
- Confusing log base rules
"""

files["probability.txt"] = """PROBABILITY FORMULAS AND CONCEPTS

1. BASIC PROBABILITY
P(A) = favorable outcomes / total outcomes
0 <= P(A) <= 1
P(A') = 1 - P(A)  [complement rule]

2. ADDITION RULE
P(A union B) = P(A) + P(B) - P(A intersection B)
For mutually exclusive events: P(A union B) = P(A) + P(B)

3. MULTIPLICATION RULE
P(A intersection B) = P(A) * P(B|A) = P(B) * P(A|B)
For independent events: P(A intersection B) = P(A) * P(B)

4. CONDITIONAL PROBABILITY
P(A|B) = P(A intersection B) / P(B),  where P(B) != 0

5. BAYES THEOREM
P(A|B) = P(B|A) * P(A) / P(B)
P(B) = P(B|A)*P(A) + P(B|A')*P(A')  [total probability]

6. COMBINATORICS
Permutation (order matters): P(n,r) = n! / (n-r)!
Combination (order doesn't matter): C(n,r) = n! / (r! * (n-r)!)
With repetition: n^r arrangements

7. BINOMIAL DISTRIBUTION
P(X=k) = C(n,k) * p^k * (1-p)^(n-k)
Mean = np
Variance = np(1-p)
Standard deviation = sqrt(np(1-p))

8. GEOMETRIC DISTRIBUTION
P(X=k) = (1-p)^(k-1) * p   [first success on kth trial]
Mean = 1/p

9. EXPECTED VALUE AND VARIANCE
E(X) = sum of x * P(X=x)
E(aX + b) = aE(X) + b
Var(X) = E(X^2) - [E(X)]^2
Var(aX + b) = a^2 * Var(X)

SOLUTION TEMPLATES FOR PROBABILITY

Template A - Counting Problems:
1. Identify total sample space size
2. Count favorable outcomes systematically
3. Apply combinations or permutations
4. Compute ratio = favorable / total

Template B - Conditional Probability:
1. Identify the given condition
2. Reduce sample space to satisfy condition
3. Count favorable outcomes in reduced space
4. Compute P = favorable / reduced total

Template C - Bayes Problems:
1. List all hypotheses H1, H2, ...
2. Find prior probabilities P(Hi)
3. Find likelihoods P(E|Hi)
4. Apply Bayes: P(Hi|E) = P(E|Hi)*P(Hi) / sum[P(E|Hj)*P(Hj)]

COMMON MISTAKES IN PROBABILITY
- Confusing permutation with combination
- Not checking independence before multiplying
- Forgetting complement rule shortcut
- Double counting in union problems
- Forgetting to reduce sample space in conditional problems
"""

files["calculus.txt"] = """CALCULUS - LIMITS, DERIVATIVES, INTEGRATION, OPTIMIZATION

1. STANDARD LIMITS
lim_{x->0} sin(x)/x = 1
lim_{x->0} tan(x)/x = 1
lim_{x->0} (1 - cos(x))/x = 0
lim_{x->0} (1 - cos(x))/x^2 = 1/2
lim_{x->0} (e^x - 1)/x = 1
lim_{x->0} (a^x - 1)/x = ln(a)
lim_{x->0} ln(1+x)/x = 1
lim_{x->inf} (1 + 1/x)^x = e
lim_{x->0} (1 + x)^(1/x) = e

2. L'HOPITAL'S RULE
If limit gives 0/0 or inf/inf form:
lim f(x)/g(x) = lim f'(x)/g'(x)
Apply repeatedly if still indeterminate.

3. DERIVATIVES - BASIC RULES
d/dx(x^n) = n * x^(n-1)
d/dx(e^x) = e^x
d/dx(a^x) = a^x * ln(a)
d/dx(ln x) = 1/x
d/dx(log_a x) = 1/(x * ln a)
d/dx(sin x) = cos x
d/dx(cos x) = -sin x
d/dx(tan x) = sec^2(x)
d/dx(cot x) = -csc^2(x)
d/dx(sec x) = sec(x)*tan(x)
d/dx(csc x) = -csc(x)*cot(x)

4. DERIVATIVE RULES
Product rule: (uv)' = u'v + uv'
Quotient rule: (u/v)' = (u'v - uv') / v^2
Chain rule: d/dx f(g(x)) = f'(g(x)) * g'(x)

5. OPTIMIZATION
Steps:
1. Define variable and objective function f(x)
2. Express in terms of one variable using constraints
3. Find f'(x) = 0 to get critical points
4. Second derivative test: f''(x) < 0 -> local max, f''(x) > 0 -> local min
5. Check boundary values
6. Compare all values for global extrema

6. INTEGRATION - STANDARD FORMS
integral x^n dx = x^(n+1)/(n+1) + C   (n != -1)
integral 1/x dx = ln|x| + C
integral e^x dx = e^x + C
integral a^x dx = a^x/ln(a) + C
integral sin(x) dx = -cos(x) + C
integral cos(x) dx = sin(x) + C
integral sec^2(x) dx = tan(x) + C

Fundamental Theorem: integral_a^b f(x)dx = F(b) - F(a)

7. INTEGRATION TECHNIQUES
Substitution: let u = g(x), then du = g'(x)dx
By parts: integral u dv = uv - integral v du

SOLUTION TEMPLATES

Template - Evaluating Limits:
1. Try direct substitution
2. If 0/0: factor and cancel, or rationalize, or L'Hopital
3. If inf/inf: divide by highest power, or L'Hopital
4. Check one-sided limits if needed

Template - Optimization Word Problem:
1. Assign variables, write objective function
2. Write constraint equation
3. Substitute constraint into objective (one variable only)
4. Differentiate, set = 0, solve
5. Verify with second derivative test
6. Answer the question in context

COMMON MISTAKES IN CALCULUS
- Forgetting chain rule in composite functions
- Not checking endpoints in closed-interval optimization
- Applying L'Hopital when form is NOT 0/0 or inf/inf
- Sign errors in integration
- Forgetting absolute value in ln|x|
"""

files["linear_algebra.txt"] = """LINEAR ALGEBRA BASICS

1. MATRIX OPERATIONS
Addition: (A+B)_ij = A_ij + B_ij  (same dimensions required)
Scalar multiplication: (kA)_ij = k * A_ij
Matrix multiplication: (AB)_ij = sum_k A_ik * B_kj
NOTE: AB != BA in general (non-commutative)
Transpose: (A^T)_ij = A_ji
(AB)^T = B^T * A^T

2. DETERMINANTS
2x2: det[[a,b],[c,d]] = ad - bc
3x3: cofactor expansion along first row:
det(A) = a11*M11 - a12*M12 + a13*M13
where Mij = minor (det of submatrix after removing row i, col j)

Properties of determinants:
- det(AB) = det(A) * det(B)
- det(A^T) = det(A)
- det(kA) = k^n * det(A)  for n x n matrix
- If two rows are equal: det = 0
- Swapping two rows: det changes sign
- Adding multiple of one row to another: det unchanged

3. INVERSE MATRIX
A^{-1} exists if and only if det(A) != 0  (A is non-singular)
2x2 inverse: [[a,b],[c,d]]^{-1} = 1/(ad-bc) * [[d,-b],[-c,a]]
Property: A * A^{-1} = A^{-1} * A = I (identity matrix)
(AB)^{-1} = B^{-1} * A^{-1}

4. SYSTEM OF LINEAR EQUATIONS Ax = b
Unique solution: det(A) != 0  -> x = A^{-1} * b
Cramer's rule: x_i = det(A_i) / det(A)
  where A_i = A with column i replaced by b
No unique solution: det(A) = 0

Row reduction (Gaussian elimination):
- Write augmented matrix [A|b]
- Use row operations to reach row echelon form
- Back-substitute to find solution

5. EIGENVALUES AND EIGENVECTORS
Definition: Av = lambda*v  where v != 0
Characteristic equation: det(A - lambda*I) = 0
For 2x2: lambda^2 - trace(A)*lambda + det(A) = 0

Properties:
- trace(A) = sum of diagonal entries = sum of eigenvalues
- det(A) = product of eigenvalues
- Eigenvectors for different eigenvalues are linearly independent

To find eigenvector for eigenvalue lambda:
Solve (A - lambda*I)v = 0

6. RANK AND NULLITY
Rank = number of linearly independent rows (or columns)
Nullity = number of free variables in Ax = 0
Rank-Nullity theorem: rank(A) + nullity(A) = number of columns
System Ax = b is consistent iff rank(A) = rank([A|b])

COMMON MISTAKES IN LINEAR ALGEBRA
- Matrix multiplication is NOT commutative
- Inverse only exists for square non-singular matrices
- Scaling a row multiplies determinant by that scalar
- Eigenvectors are not unique (any scalar multiple works)
- Not verifying det != 0 before finding inverse
"""

files["solution_templates.txt"] = """JEE MATH SOLUTION STRATEGIES AND TEMPLATES

GENERAL PROBLEM-SOLVING FRAMEWORK
1. Read carefully - identify what is GIVEN and what is ASKED
2. Identify the topic/domain (algebra, calculus, probability, etc.)
3. Recall relevant formulas for that topic
4. Plan solution steps BEFORE computing
5. Execute calculations step by step showing all work
6. VERIFY the answer (domain, sign, units, reasonableness)

ALGEBRA TEMPLATES

Template A: Quadratic Problems
Given: equation or conditions on roots
Step 1: Write as ax^2 + bx + c = 0
Step 2: Compute D = b^2 - 4ac, check nature of roots
Step 3: Use Vieta's if sum/product of roots needed
Step 4: Use quadratic formula for exact roots

Template B: Sequence and Series
Given: AP or GP sequence
Step 1: Identify type - check constant differences (AP) or ratios (GP)
Step 2: Extract first term and common difference/ratio
Step 3: Apply nth term or sum formula

Template C: Inequalities
Step 1: Move everything to one side
Step 2: Find critical points (zeros of numerator and denominator)
Step 3: Test intervals using sign chart
Step 4: State solution with correct brackets

PROBABILITY TEMPLATES

Template A: Basic Counting
Step 1: Define sample space clearly and count total outcomes
Step 2: List favorable outcomes systematically (use combinations)
Step 3: P = favorable / total
Step 4: Check answer is between 0 and 1

Template B: Conditional Probability
Step 1: Identify the conditioning event
Step 2: Reduce sample space to that event
Step 3: Count favorable within reduced space
Step 4: Compute ratio

Template C: Bayes Theorem
Step 1: Identify all mutually exclusive hypotheses
Step 2: Write prior probabilities P(Hi)
Step 3: Write likelihoods P(Evidence | Hi) for each
Step 4: Apply Bayes formula
Step 5: Verify posteriors sum to 1

CALCULUS TEMPLATES

Template A: Limit Evaluation
Step 1: Try direct substitution first
Step 2: If 0/0: try factoring, rationalizing, or standard limits
Step 3: If still stuck: apply L'Hopital's rule
Step 4: Check if one-sided limits differ

Template B: Optimization
Step 1: Define variables and objective function
Step 2: Express in one variable using constraint
Step 3: Differentiate, set f'(x) = 0
Step 4: Second derivative test for max/min
Step 5: Check boundary conditions
Step 6: State answer in context of problem

Template C: Integration
Step 1: Identify technique (direct, substitution, by parts)
Step 2: For substitution: choose u, find du
Step 3: Transform integral entirely in u
Step 4: Integrate and back-substitute
Step 5: For definite integral: apply limits after

LINEAR ALGEBRA TEMPLATES

Template A: Solving System Ax = b
Step 1: Write augmented matrix [A|b]
Step 2: Row reduce to echelon form
Step 3: Check consistency (rank conditions)
Step 4: Back-substitute for solution

Template B: Finding Eigenvalues/Eigenvectors
Step 1: Set up det(A - lambda*I) = 0
Step 2: Expand and solve characteristic polynomial
Step 3: For each lambda, solve (A - lambda*I)v = 0
Step 4: Express eigenvector as free parameter

VERIFICATION CHECKLIST
After solving, always verify:
[ ] Probability: 0 <= P <= 1
[ ] Log: argument is positive
[ ] Square root: result is non-negative
[ ] Division: denominator != 0
[ ] Optimization: it's truly a max/min (second derivative test)
[ ] Quadratic: check roots satisfy original equation
[ ] Matrix inverse: det != 0

COMMON JEE TRICK QUESTION PATTERNS
1. Probability > 1 trap: always verify final P is valid
2. Determinant = 0 trap: check before using Cramer's rule
3. Log domain trap: argument must be strictly positive
4. Square root trap: sqrt(x^2) = |x|, not just x
5. Division by variable: consider case when variable = 0
6. Infinite GP: valid only when |r| < 1
7. AP/GP confusion: always verify constant difference vs ratio
"""

for filename, content in files.items():
    path = KB / filename
    path.write_text(content, encoding="utf-8")
    print(f"Written: {filename}  ({len(content)} bytes)")

print("\nAll knowledge base files populated successfully!")
print("Now run: streamlit run app.py")