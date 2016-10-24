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


inline const int rnd(const int start, const int end) {
    static random_device rnd;
    static mt19937 mt(rnd());
    uniform_int_distribution<> ud(start, end);
    return ud(mt);
}

typedef vector<int> Pack;
typedef vector<int> Board;


class Game {
private:
    auto rot1(Pack& pack) {
        Pack p(pack.size());
        for(int i = 0; i < pack.size(); ++i) {
            int x = i % PS, y = i / PS;
            p[i] = pack[y + (PS - 1 - x) * PS];
        }
        return move(p);
    }
public:
    const int W, H, PS, SUM, TURN, EMPTY, OBSTACLE;
    vector<Pack> packs;

    Game(const int w, const int h, const int ps, const int sum, const int turn, vector<Pack> packs_)
            : W(w), H(h), PS(ps), SUM(sum), TURN(turn), EMPTY(0), OBSTACLE(sum + 1), packs(turn * 4) {
        // 予め回転させたものを用意
        for(int i = 0; i < packs_.size(); ++i) {
            packs[i * 4] = rot1(packs_[i]);
            for(int k = 1; k < 4; ++k) {
                auto j = i * 4 + k;
                packs[j] = rot1(packs[j - 1]);
            }
        }
    }

    auto inputBoard() {
        int bw = W + (PS - 1) * 2, bh = H + PS + 2;
        Board b(bw * bh);
        for(int i = 0; i < bw; ++i) {
            b[i] = OBSTACLE;
            b[i + (bh - 1) * bw] = OBSTACLE;
        }
        for(int j = 1; j < bh - 1; ++j) {
            for(int k = 0; k < PS - 1; ++k) {
                b[j * bw + k] = OBSTACLE;
                b[j * bw + bw - k - 1] = OBSTACLE;
            }
        }
        int temp;
        string end_;
        for(int j = 0; j < H; ++j) {
            for(int i = 0; i < W; ++i) {
                cin >> temp;
                b[(PS - 1 + i) + (1 + PS + j) * bw] = temp;
            }
        }
        cin >> end_;
        return move(b);
    }

    auto solve(int turn, int remain, int ob, Board b, int eob, Board eb) {
        auto r1 = rnd(0, W - PS);
        auto r2 = rnd(0, 3);
        // TODO:
        return make_tuple(r1, r2);
    }
};


auto initialInput() {
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
    cout.flush();
    return true;
}


int main() {
    ios::sync_with_stdio(false);
    cout << AI_NAME << endl; cout.flush();
    auto game = initialInput();
    while(true) {
        if(!processTurn(game)) break;
    }
    return 0;
}
