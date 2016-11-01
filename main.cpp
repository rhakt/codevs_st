#include <iostream>
#include <string>
#include <vector>
#include <tuple>
#include <cmath>
#include <functional>
#include <chrono>
#include <unordered_map>
#include <queue>
#include <random>
#include <algorithm>


using namespace std;

static const string AI_NAME = "efutea";
static const int INF = 1 << 16;


inline int rnd(const int range) {
    static random_device rd;
    static mt19937 mt(rd());
    static uniform_real_distribution<> ud(0, 1);
    return static_cast<int>(floor(ud(mt) * range));
}


template <class T>
inline void uniq(vector<T>& vec) {
	sort(vec.begin(), vec.end());
	vec.erase(unique(vec.begin(), vec.end()), vec.end());
}


typedef vector<int> Pack;
typedef vector<int> Board;
typedef pair<int, int> Pii;
typedef tuple<int, int, int, int, int> Action;


struct Result {
	int score;
	int pscore;
	int chain;
	Board board;
	vector<int> next;
};

struct Score {
	int score;
	int ob;
	int pscore;
	int chain;
	vector<int> next;
	Board board;
	Action hist;
	explicit Score(const Board& b, int ob_ = 0) : score(0), board(b), ob(ob_), pscore(0), chain(0) {}
	Score(Score& s, Result&& r, const int pos, const int rot, int ob_) {
		score = r.score;// +s.score;
		pscore = r.pscore;
		chain = r.chain;
		board = move(r.board);
		s.next = move(r.next);
		ob = max(0, ob_ - (int)(r.pscore * 0.2f));
		hist = make_tuple(pos, rot, r.chain, r.pscore, ob);
	}
	Score(Score& s, Result&& r, int ob_) {
		score = r.score;// +s.score;
		pscore = r.pscore;
		chain = r.chain;
		board = move(r.board);
		s.next = move(r.next);
		ob = max(0, ob_ - (int)(r.pscore * 0.2f));
		hist = s.hist;
	}
};

struct ScoreComp {
	bool operator() (const Score& l, const Score& r) {
		return l.score < r.score;
	}
};


class Game {
private:
    inline Pack rot1(const Pack& pack) {
        Pack p(pack.size());
        for(int i = 0; i < pack.size(); ++i) {
            int x = i % PS, y = i / PS;
            p[i] = pack[y + (PS - 1 - x) * PS];
        }
        return move(p);
    }

    inline Pack rotatePack(const Pack& pack, int rot) {
        Pack p = pack;
        while(rot > 0) {
            p = rot1(p);
            --rot;
        }
        return move(p);
    }

    inline int fillObstacle(Pack& pack, int num) {
        for(auto&& p : pack) {
            if(num <= 0) break;
            if(p != EMPTY) continue;
            p = OBSTACLE;
            num -= 1;
        }
        return num;
    }

    inline bool isFallable(const Pack& pack, const int pos) {
        if(pos < 0) {
            for(int k = 0; k < -pos; ++k) {
                for(int i = 0; i < PS; ++i) {
                    if(pack[k + i * PS] != EMPTY) return false;
                }
            }
        } else if(W - PS < pos) {
            for(int k = PS - 1; k > W - pos - 1; --k) {
                for(int i = 0; i < PS; ++i) {
                    if(pack[k + i * PS] != EMPTY) return false;
                }
            }
        }
        return true;
    }

	inline vector<Pii> forceGravity(Board& board, vector<int>& update) {
		vector<Pii> lst;
		uniq(update);
		for (auto& x : update) {
			int j = BH - 2;
			int e = -1;
			while (j > 0) {
				if (e == -1 && board[x + j * BW] == EMPTY) {
					e = j;
				} else if (e != -1 && board[x + j * BW] != EMPTY) {
					swap(board[x + j * BW], board[x + e * BW]);
					lst.emplace_back(x, e);
					j = e;
					e = -1;
				} else if (j <= PS && board[x + j * BW] != EMPTY) {
					lst.emplace_back(x, j);
				}
				--j;
			}
		}
		return move(lst);
	}

	inline vector<Pii> forceGravity(Board& board, const Pack& pack, const int pos) {
		vector<int> update;
		for (int i = 0; i < pack.size(); ++i) {
			if (pack[i] == EMPTY) continue;
			int x = i % PS, y = i / PS;
			board[pos + x + 1 + (y + 1) * BW] = pack[i];
			update.push_back(pos + x + 1);
		}
		return move(forceGravity(board, update));
	}

	inline int anniLine(const Board& b, Board& board, int sx, int sy, int dx, int dy, vector<int>& update) {
		int anni = 0;
		int start = 0, last = 0, sum = 0;
		int idx = sx + sy * BW;
		while (EMPTY < b[idx] && b[idx] < OBSTACLE) {
			++last;
			sum += b[idx];
			while (sum > SUM) {
				sum -= b[sx + start * dx + (sy + start * dy) * BW];
				++start;
			}
			if (sum == SUM) {
				anni += (last - start);
				for (int k = start; k < last; ++k) {
					board[sx + k * dx + (sy + k * dy) * BW] = EMPTY;
					update.push_back(sx + k * dx);
				}
			}
			idx += dx + dy * BW;
		}
		return anni;
	}

	inline tuple<int, vector<Pii>> anniBoard(Board& board, vector<Pii>& update) {
		int anni = 0;
		vector<tuple<int, int, int, int>> lst;
		vector<Pii> dir = { {1, 0}, {0, 1}, {1, 1}, {1, -1} };
		const Board b = board;
		for (auto&& u : update) {
			const int bx = u.first, by = u.second;
			int sx, sy;

			sx = bx - 1;
			sy = by;
			while (EMPTY < b[sx + by * BW] && b[sx + by * BW] < OBSTACLE) --sx;
			lst.emplace_back(sx + 1, sy, 1, 0);

			sx = bx;
			sy = by - 1;
			while (EMPTY < b[sx + sy * BW] && b[sx + sy * BW] < OBSTACLE) --sy;
			lst.emplace_back(sx, sy + 1, 0, 1);

			sx = bx - 1;
			sy = by - 1;
			while (EMPTY < b[sx + sy * BW] && b[sx + sy * BW] < OBSTACLE) { --sx; --sy; }
			lst.emplace_back(sx + 1, sy + 1, 1, 1);

			sx = bx - 1;
			sy = by + 1;
			while (EMPTY < b[sx + sy * BW] && b[sx + sy * BW] < OBSTACLE) { --sx; ++sy; }
			lst.emplace_back(sx + 1, sy - 1, 1, -1);
		}
		vector<int> anniList;
		uniq(lst);
		for (auto&& l : lst) {
			anni += anniLine(b, board, get<0>(l), get<1>(l), get<2>(l), get<3>(l), anniList);
		}
		return make_tuple(anni, forceGravity(board, anniList));
	}

	inline void checkAround(const Board& b, const int x, const int y, vector<int>& around) {
		static vector<int> dir = { 1, BW - 1, BW + 1, BW };
		for (auto&& a : around) a = 0;
		const int idx = x + y * BW;
		for (auto&& d : dir) {
			int s, l = 0, sum = 0;
			for (s = -1; ; --s) {
				int num = b[idx + s * d];
				if (EMPTY == num || num == OBSTACLE) break;
				if (sum + num >= SUM) break;
				sum += num;
			}
			++s;
			while (s <= 0) {
				if (sum < SUM) { 
					if(sum > 0) around[SUM - sum - 1] += 1;
					++l;
					int num = b[idx + l * d];
					if (num == EMPTY || num == OBSTACLE) break;
					sum += num;
				} else {
					sum -= b[idx + s * d];
					++s;
				}
			}
		}
	}

	inline tuple<int, int> fowardBoard(Board& board, vector<Pii>& update) {
		int chain = 0, pscore = 0;
		while (true) {
			auto res = anniBoard(board, update);
			auto anni = get<0>(res);
			update = move(get<1>(res));
			if (anni == 0) break;
			++chain;
			pscore += powCache[chain - 1] * (int)(anni * 0.5f);
		}
		return make_tuple(pscore, chain);
	}

	inline tuple<int, int> tryBoard(Board board, const int x, const int y, const int num) {
		board[x + y * BW] = num;
		vector<Pii> update = { {x, y} };
		return fowardBoard(board, update);
	}

	inline void packInclude(int turn, vector<int>& inc, int k = 4) {
		for (auto&& i : inc) i = 0;
		for (int i = 1; i <= k; ++i) {
			const Pack& pack = packs[(turn + i) * 4];
			for (auto&& p : pack) {
				if (EMPTY < p && p < OBSTACLE && !inc[p - 1]) inc[p - 1] = i;
			}
		}
	}

	inline int evaluateBlock(const Board& board) {
		static vector<int> dir = { -1 - BW * 2, 1 - BW * 2 };
		int s = 0;
		for (int x = 1; x < BW - 1; ++x) {
			for (int y = BH - 2; y > PS; --y) {
				int idx = x + y * BW, k = 0;
				int n = board[idx];
				if (n == EMPTY) break;
				if (n == OBSTACLE) continue;
				for (auto&& d : dir) {
					if (idx + d < 0) continue;
					if (board[idx + d] + n == SUM) ++k;
				}
				s += k;
			}
		}
		return s;
	}

	inline Result evaluateBoard(int turn, Board board, const Pack& pack, const int pos, int ob, const tuple<int, int, int>& eneinfo, const vector<int>& next, int remain) {
		static vector<int> hei(W), ghei(W), around(SUM - 1), prev(W), inc(SUM - 1);
		static int theat = 0;
		
		auto update = forceGravity(board, pack, pos);		
		
		int pscore = 0, chain = 0;
		tie(pscore, chain) = fowardBoard(board, update);

		for (int x = 1; x < BW - 1; ++x) {
			if (board[x + PS * BW] != EMPTY)
				return { -INF, pscore, chain, move(board)};
		}

		int ech, esc, ct;
		tie(esc, ech, ct) = eneinfo;
		if (ct == turn && ech >= 13 && (esc * 0.2f) <= (pscore * 0.2f)) {
			cerr << "<interrupt: ch = " << chain << ", sc = " << pscore << ">" << endl;
		}
		if (ob > 6) theat = 0;
		else  theat = max(theat, esc);

		int sf = (int)(pscore * 0.2f);
		
		int hpena = 0, hpena2 = 0;
		for (int x = 1; x < BW - 1; ++x) {
			int h = 0;
			for (int y = BH - 2; y > PS; --y) {
				if (board[x + y * BW] == EMPTY) break;
				++h;
			}
			hei[x - 1] = h;
			if (x > 1) {
				ghei[x - 2] = hei[x - 1] - hei[x - 2];
				hpena += (int)pow(max(0, abs(ghei[x - 1]) - 3), 2);
				ghei[x - 2] = abs(ghei[x - 2]) < 4 ? 0 : ghei[x - 2];
			}
		}
		ghei[W - 1] = 5;
		int neg = 0;
		for (int x = 1; x < BW - 1; ++x) {
			if (ghei[x - 1] < 0) neg = x;
			else if (ghei[x - 1] > 0) {
				hpena2 += (int)pow(x - neg < PS ? PS - (x - neg) : 0, 2);
			}
		}
		
		vector<int> next2;
		for (auto&& p : prev) p = 0;
		for (auto&& nx : next) {
			int x = nx >> 4, n = nx & 0xF;
			prev[x - 1] |= (1 << (n - 1));
		}
		int next_ch = 0;
		int next_sc = 0;
		packInclude(turn, inc);
		for (int x = 1; x < BW - 1; ++x) {
			if (x - 2 > 0 && hei[x - 2] == 0) continue;
			if (x < W && hei[x] == 0) continue;
			if (x < pos - 1 || pos + PS < x) {
				if (next.size() > 0 && !prev[x - 1]) continue;
			}
			auto y = BH - 2 - hei[x - 1];
			checkAround(board, x, y, around);
			for (int n = 1; n <= SUM - 1; ++n) {
				if (around[n - 1] < 1) continue;
				if (!inc[n - 1]) continue;
				if (x < pos - 1 || pos + PS < x) {
					if (next.size() > 0 && !(prev[x - 1] & (1 << (n - 1)))) continue;
				}
				int sc, ch;
				tie(sc, ch) = tryBoard(board, x, y, n);
				if (ch > 0) {
					next2.push_back(x << 4 | n);
				}
				//int t = (int)(sc / powCache[inc[n - 1] - 1]);
				next_ch = max(next_ch, ch);
				next_sc = max(next_sc, sc);
			}
		}
		
		const int sfd = (int)(theat * 1.69f * 0.2f) + ob;
		const int th = remain < 30000 ? (remain < 10000 ? 30 : 60) : min(sfd + W * H, W * H * 2);
		if (sf >= th) { return{ INF + pscore, pscore, chain, move(board), move(next2) }; }

		
		int score = 0;
			
		//if (chain > 15)
		//	cerr << "emittable: " << chain << " (" << sf << ")" << endl;

		score += 200 * max(next_ch, chain);
		//score += max(pscore, (int)(next_sc * 0.77f));
		score += max(pscore, next_sc);
		score += pscore < 5 ? -pscore * 2 : 0;
		score -= hpena + hpena2;
		score += evaluateBlock(board);
		return {score, pscore, chain, move(board), move(next2)};
	}
	
	template<class F>
	inline void nextPacks(const int turn, const int ob, const F& func) {
		if (ob > 0) {
			Pack p = packs[turn * 4];
			const int num = fillObstacle(p, ob);
			for (int rot = 0; rot < 4; ++rot) {
				for (int pos = -2; pos < W; ++pos) {
					if (isFallable(p, pos)) func(p, pos, rot, num);
				}
				if (rot > 2) break;
				p = rot1(p);
			}
			return;
		}
		for (int rot = 0; rot < 4; ++rot) {
			const Pack& p = packs[turn * 4 + rot];
			for (int pos = -2; pos < W; ++pos) {
				if (isFallable(p, pos)) func(p, pos, rot, 0);
			}
		}
	}

	vector<Pack> packs;
	vector<int> powCache;
	queue<Action> actCache;

public:
    const int W, H, PS, SUM, TURN, EMPTY, OBSTACLE;
    const int BW, BH;
    
    Game(const int w, const int h, const int ps, const int sum, const int turn, const vector<Pack>& packs_)
            : W(w), H(h), PS(ps), SUM(sum), TURN(turn), EMPTY(0), OBSTACLE(sum + 1), packs(turn * 4),
              BW(W + 2), BH(H + PS + 2), powCache(50) {
        for(int i = 0; i < packs_.size(); ++i) {
            packs[i * 4] = packs_[i];
            for(int k = 1; k < 4; ++k) {
                auto j = i * 4 + k;
                packs[j] = rot1(packs[j - 1]);
            }
        }
		auto k = 1.3f;
		for (auto&& pc : powCache) {
			pc = (int)k;
			k *= 1.3f;
		}
    }

    Board inputBoard() {
        Board b(BW * BH);
        for(int i = 0; i < BW; ++i) {
            b[i] = OBSTACLE;
            b[i + (BH - 1) * BW] = OBSTACLE;
        }
        for(int j = 1; j < BH - 1; ++j) {
            b[j * BW] = OBSTACLE;
            b[j * BW + BW - 1] = OBSTACLE;
        }
        int temp;
        string end_;
        for(int j = 0; j < H; ++j) {
            for(int i = 0; i < W; ++i) {
                cin >> temp;
                b[(1 + i) + (1 + PS + j) * BW] = temp;
            }
        }
        cin >> end_;
        return move(b);
    }

    tuple<int, int> solve(const int turn, const int remain, const int ob, const Board& b, const int eob, const Board& eb) {
		static int psc = 0;
		static vector<int> hei(W);
		static vector<int> around(SUM - 1);
		
		auto limit = min(remain, 20000);
		auto start = chrono::system_clock::now();

		cerr << "[" << turn << "] ob: " << ob << " remain:" << remain << "\n";

		tuple<int, int, int> eneinfo = make_tuple(0, 0, turn);
		if( ob < 7 ) {
			int next_ch = 0;
			int next_sc = 0;
			nextPacks(turn, eob, [&](const Pack& p, const int pos, const int rot, const int nob) {
				Board eb_ = eb;
				auto update = forceGravity(eb_, p, pos);
				int sc, ch;
				tie(sc, ch) = fowardBoard(eb_, update);
				for (int x = 1; x < BW - 1; ++x) {
					if (eb[x + PS * BW] != EMPTY) return;
				}
				next_ch = max(next_ch, ch);
				next_sc = max(next_sc, sc);
			});
			eneinfo = make_tuple(next_sc, next_ch, turn);
			if(next_ch >= 13)
				cerr << "<predicate: ch = " << next_ch << ", sc = " << next_sc << ">\n";
		}

		const int k = turn < 20 ? 6 : (remain < 30000 ? (remain < 10000 ? 2 : 3) : 6);
		const int beam = 200;

		priority_queue<Score, vector<Score>, ScoreComp> pq;
		pq.emplace(b, ob);
		
		for(int t = turn; t <= min(turn + k, TURN - 1) && !pq.empty(); ++t) {
			int pob = 0;
			if (t == turn && get<0>(eneinfo) >= 250) {
				pob = (int)(get<0>(eneinfo) * 0.2f);
			}
			priority_queue<Score, vector<Score>, ScoreComp> npq;
			int count = beam;
			while (!pq.empty() && count) {
				auto st = pq.top();
				pq.pop();
				if (st.score < -INF + 1 && count == beam) {
					npq.push(st);
					break;
				}
				if (st.score < -INF + 1) break;
				if (st.score > INF - 1) {
					npq.push(st);
					break;
				}
				--count;
				if (st.pscore >= 250) {
					npq.push(st);
					continue;
				}
				nextPacks(t, st.ob, [&](const Pack& p, const int pos, const int rot, int nob) {
					nob += pob;
					auto res = evaluateBoard(t, st.board, p, pos, nob, eneinfo, st.next, remain);
					if(t == turn)
						npq.emplace(st, move(res), pos, rot, nob);
					else
						npq.emplace(st, move(res), nob);
				});
			}
			pq = move(npq);
		}

		if (pq.empty()) {
			return make_tuple(0, 0);
		}

		int pos = 0, rot = 0, chain = 0, pscore = 0, temp = 0, count = 10;
		auto st = pq.top();
		tie(pos, rot, chain, pscore, ignore) = st.hist;

		psc += pscore;
		if (chain > 0)
			cerr << "chain: " << chain << " score: " << psc << "\n";
		
		//auto diff = std::chrono::system_clock::now() - start;
		//auto ms = chrono::duration_cast<chrono::milliseconds>(diff).count();
		//if(ms > 2000)
		//	cerr << "time = " << ms << " msec." << endl;
		cerr.flush();
		
        return make_tuple(pos, rot);
    }
};


Game initialInput() {
    int w, h, ps, sum, turn, temp;
    string end_;
    cin >> w >> h >> ps >> sum >> turn;
    vector<Pack> packs(turn);
    for(auto& p : packs) {
        p.resize(ps * ps);
        for(auto &pp : p) {
            cin >> temp;
            pp = temp;
        }
        cin >> end_;
    }
    return move(Game(w, h, ps, sum, turn, move(packs)));
}


bool processTurn(Game& game) {
    int pos = 0, rot = 0;
    int turn, remain, ob, eob;
    cin >> turn >> remain >> ob;
    auto b = game.inputBoard();
    cin >> eob;
    auto eb = game.inputBoard();
	ob = max(ob - eob, 0);
	eob = max(eob - ob, 0);
    tie(pos, rot) = game.solve(turn, remain, ob, b, eob, eb);
    cout << pos << " " << rot << endl;
    return true;
}


int main() {
    ios::sync_with_stdio(false);
    cout << AI_NAME << endl;
    auto game = initialInput();
    while(processTurn(game));
    return 0;
}
