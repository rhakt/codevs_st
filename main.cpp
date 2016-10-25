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

#define POS_HASH(x, y) (x * 100 + y)
#define LINE_HASH(x, y, dx, dy) (x * 10000, y * 100 + dx * 10 + dy)


using namespace std;

static const string AI_NAME = "efutea";


inline int rnd(const int range) {
    static random_device rd;
    static mt19937 mt(rd());
    static uniform_real_distribution<> ud(0, 1);
    return static_cast<int>(floor(ud(mt) * range));
}


inline void uniq(vector<int>& vec) {
	sort(vec.begin(), vec.end());
	vec.erase(unique(vec.begin(), vec.end()), vec.end());
}


typedef vector<int> Pack;
typedef vector<int> Board;


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

	inline tuple<int, vector<int>> anni_board(Board& board, vector<int>& update) {
		int anni = 0;
		vector<int> lst;
		Board b = board;


		return make_tuple(anni, lst);
	}

	inline vector<int> forceGravity(Board& board, vector<int>& update) {
		vector<int> lst;
		uniq(update);
		for (auto& x : update) {
			int j = H - 2;
			int e = -1;
			while (j > 0) {
				if (e == -1 && board[x + j * BW] == EMPTY) {
					e = j;
				} else if (e != -1 && board[x + j * BW] != EMPTY) {
					swap(board[x + j * BW], board[x + e * BW]);
					lst.push_back(POS_HASH(x, e));
					j = e;
					e = -1;
				}
			}
		}
		return move(lst);
	}

	inline vector<int> forceGravity(Board& board, const Pack& pack, const int pos) {
		vector<int> update;
		for (int i = 0; i < pack.size(); ++i) {
			if (pack[i] == EMPTY) continue;
			int x = i % PS, y = i / PS;
			board[pos + x + 1 + (y + 1) * BW] = pack[i];
			update.push_back(pos + x + 1);
		}
		return forceGravity(board, update);
	}


public:
    const int W, H, PS, SUM, TURN, EMPTY, OBSTACLE;
    const int BW, BH;
    vector<Pack> packs;

    Game(const int w, const int h, const int ps, const int sum, const int turn, const vector<Pack>& packs_)
            : W(w), H(h), PS(ps), SUM(sum), TURN(turn), EMPTY(0), OBSTACLE(sum + 1), packs(turn * 4),
              BW(W + 2), BH(H + PS + 2) {
        for(int i = 0; i < packs_.size(); ++i) {
            packs[i * 4] = packs_[i];
            for(int k = 1; k < 4; ++k) {
                auto j = i * 4 + k;
                packs[j] = rot1(packs[j - 1]);
            }
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
        fillObstacle(p, rob);

        while(!isFallable(rotatePack(p, r2), r1)) {
            r1 = rnd(W + 1) - 2;
            r2 = rnd(4);
        }

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
