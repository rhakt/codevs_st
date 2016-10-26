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
static const int INF = 1 << 30;


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
};

struct Score {
	int score;
	int ob;
	Board board;
	vector<Action> hist;
	explicit Score(const Board& b, int ob_ = 0) : score(0), board(b), ob(ob_) {}
	Score(Score& s, Result&& r, const int pos, const int rot, int ob_) {
		score = r.score + s.score;
		board = move(r.board);
		ob = max(0, ob_ - (int)floor(r.pscore * 0.2f));
		hist = s.hist;
		hist.emplace_back(pos, rot, r.chain, r.pscore, ob);
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
		return forceGravity(board, update);
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

	inline int checkAround(const Board& b, const int x, const int y) {
		static vector<int> dir = { -1, 1, BW, -BW-1, -BW+1, BW-1, BW+1 };
		int idx = x + y * BW;
		int minNum = 9;
		for (auto& d : dir) {
			int num = b[idx + d];
			if (EMPTY < num && num < OBSTACLE) minNum = min(num, minNum);
		}
		return SUM - minNum;
	}

	inline tuple<int, int> fowardBoard(Board& board, vector<Pii>& update) {
		int chain = 0, pscore = 0;
		while (true) {
			auto res = anniBoard(board, update);
			auto anni = get<0>(res);
			update = move(get<1>(res));
			if (anni == 0) break;
			++chain;
			pscore += powCache[chain - 1] * static_cast<int>(floor(anni * 0.5f));
		}
		return make_tuple(pscore, chain);
	}

	inline tuple<int, int> tryBoard(Board board, const int x, const int y, const int num) {
		board[x + y * BW] = num;
		vector<Pii> update = { {x, y} };
		return fowardBoard(board, update);
	}

	inline Result evaluateBoard(int turn, Board board, const Pack& pack, const int pos, int ob) {
		static vector<int> hei(W);
		
		auto update = forceGravity(board, pack, pos);		
		
		int pscore = 0, chain = 0;
		tie(pscore, chain) = fowardBoard(board, update);

		for (int x = 1; x < BW - 1; ++x) {
			if (board[x + PS * BW] != EMPTY)
				return { -INF, pscore, chain, move(board) };
		}

		int sf = (int)floor(pscore * 0.2f);
		if (sf >= 50) {
			return{ INF, pscore, chain, move(board) };
		}

		
		for (int x = 1; x < BW - 1; ++x) {
			int h = 0;
			for (int y = BH - 2; y > PS; --y) {
				if (board[x + y * BW] == EMPTY) break;
				++h;
			}
			hei[x - 1] = h;
		}
		
		int next_ch = 0;
		int next_sc = 0;
		for (int x = 1; x < BW - 1; ++x) {
			if (x - 2 > 0 && hei[x - 2] == 0) continue;
			if (x < W && hei[x] == 0) continue;
			auto y = BH - 2 - hei[x - 1];
			const int maxNum = checkAround(board, x, y);
			for (int n = 1; n <= maxNum; ++n) {
				int sc, ch;
				tie(sc, ch) = tryBoard(board, x, y, n);
				next_ch = max(next_ch, ch);
				next_sc = max(next_sc, sc);
			}
		}
		
		int score = 0;
		
		//if (max(next_ch, chain) > 16)
		//	cerr << "emittable: " << chain << " next: " << next_ch << endl;

		score += 100 * max(next_ch, chain);
		score += max(pscore, next_sc);

		return {score, pscore, chain, move(board)};
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
	bool isCache;

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
			pc = static_cast<int>(floor(k));
			k *= 1.3f;
		}
		isCache = false;
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
		/*static Board preb;
		if (turn > 0) {
			for (int i = 0; i < b.size(); ++i) {
				if (preb[i] != b[i]) cerr << "!!" << endl;
			}
		}*/

		auto limit = min(remain, 20000);
		auto start = chrono::system_clock::now();

		cerr << "[" << turn << "] " << endl;

		if (isCache && !actCache.empty()) {
			int pos, rot, chain, pscore, nob;
			tie(pos, rot, chain, pscore, nob) = actCache.front();
			actCache.pop();
			if (nob == ob) {
				psc += pscore;
				if (chain > 0)
					cerr << "chain: " << chain << " score: " << psc << " (cache)" << endl;
				return make_tuple(pos, rot);
			}
			cerr << "cache reset!!" << endl;
			actCache = queue<Action>();
		}

		const int k = 3;
		const int beam = 200;

		priority_queue<Score, vector<Score>, ScoreComp> pq;
		pq.emplace(b, ob);
		
		for(int t = turn; t <= turn + k && !pq.empty(); ++t) {
			priority_queue<Score, vector<Score>, ScoreComp> npq;
			int count = beam;
			while (!pq.empty() && count > 0) {
				auto st = pq.top();
				if (st.score < -INF + 1) break;
				if (st.score > INF - 1) {
					npq.push(st);
					break;
				}
				pq.pop();
				--count;
				nextPacks(t, st.ob, [&](const Pack& p, const int pos, const int rot, const int nob) {
					auto res = evaluateBoard(t, st.board, p, pos, nob);
					npq.emplace(st, move(res), pos, rot, nob);
				});
			}
			swap(pq, npq);
		}

		if (pq.empty()) {
			return make_tuple(0, 0);
		}

		int pos, rot, chain, pscore, nob;
		auto st = pq.top();
		tie(pos, rot, chain, pscore, nob) = st.hist[0];

		if (isCache) {
			for (auto&& act : st.hist) actCache.push(act);
			actCache.pop();
		}

		psc += pscore;
		if (chain > 0)
			cerr << "chain: " << chain << " score: " << psc << " (" << st.score << ")" << endl;
		//preb = board;

		auto diff = std::chrono::system_clock::now() - start;
		auto ms = chrono::duration_cast<chrono::milliseconds>(diff).count();
		if(ms > 1000)
			cerr << "elapsed time = " << ms << " msec." << endl;
		
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
