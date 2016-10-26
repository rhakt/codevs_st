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
typedef tuple<int, int, int> Score;


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
				}
				else if (e != -1 && board[x + j * BW] != EMPTY) {
					swap(board[x + j * BW], board[x + e * BW]);
					lst.emplace_back(x, e);
					j = e;
					e = -1;
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

	inline Score evaluateBoard(int turn, Board board, const Pack& pack, const int pos, int ob) {
		static Board preb;
		static int psc = 0;
		if (turn > 0) {
			for (int i = 0; i < board.size(); ++i) {
				if (preb[i] != board[i]) cerr << "!!" << endl;
			}
		}
		
		auto update = forceGravity(board, pack, pos);
		int score = 0, chain = 0;
		while (true) {
			auto res = anniBoard(board, update);
			auto anni = get<0>(res);
			update = move(get<1>(res));
			if (anni == 0) break;
			++chain;
			score += powCache[chain - 1] * static_cast<int>(floor(anni * 0.5f));
		}
		psc += score;
		if(chain > 0)
			cerr << "[" << turn <<  "] chain: " << chain << " score: " << psc << endl;
		preb = board;

		return {score, score, chain};
	}

public:
    const int W, H, PS, SUM, TURN, EMPTY, OBSTACLE;
    const int BW, BH;
    vector<Pack> packs;
	vector<int> powCache;

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
		auto r1 = rnd(W + 1) - 2;
        auto r2 = rnd(4);

        Pack p = packs[turn * 4];
        int rob = max(ob - eob, 0);
        int nob = fillObstacle(p, rob);

        while(!isFallable(rotatePack(p, r2), r1)) {
            r1 = rnd(W + 1) - 2;
            r2 = rnd(4);
        }

		evaluateBoard(turn, b, rotatePack(p, r2), r1, rob - nob);

        return make_tuple(r1, r2);
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
