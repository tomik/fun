/** 
 * Solution to generic message dispatching with template metaprogramming
 * We have a set of types representing messages (MsgFoo, MsgBar, etc.) 
 * and set of ids identifying these messages (MSG_FOO, MSG_BAR, etc.)
 * 
 * We want two things:
 * 1. "sending messages" : Static mapping (generates value) from type to message id (type -> value)
 * 2. "receiving messages" : Dynamic mapping (generates code) from message id to type (value -> type)
 *
 * Example usage:
 * We have a messaging protocol where each message is represented by header
 * containing message id and then binary representation of that message.
 *
 * On sending the message we need to fill the message id in the header based on the
 * message type we are holding. We use a static mapping message typ -> message id for this.
 * Naturally we could have put the message id into message itself, however this is more general
 * for instance for the case when messages are coming from a library and gives more flexibility
 * to give message types different ids in different situations.
 *
 * On message receival we parse the header and then we need to be able to decode the binary chunk 
 * based on the message id - every message knows how to deserialize itself so we use
 * the dynamic mapping message id -> type to call a templated version of the deserialiser.
 */

#include <iostream>

struct MsgFoo {
};

void PrintMsg(MsgFoo) {
  std::cout << "MsgFoo" << std::endl;
}

struct MsgBar {
};

void PrintMsg(MsgBar) {
  std::cout << "MsgBar" << std::endl;
}

struct MsgBaz {
};

enum MsgId {
  MSG_BAR,
  MSG_FOO,
  MSG_BAZ,
};

std::ostream& operator<<(std::ostream& os, MsgId msgId) {
  switch (msgId) {
    case MSG_BAR: 
      os << "MSG_BAR";
      break;

    case MSG_FOO: 
      os << "MSG_FOO";
      break;
  }
  return os;
}


template<int n> struct MsgPair {};

template<> struct MsgPair<1> {
  typedef MsgFoo type;
  enum { id = MSG_FOO };
};

template<> struct MsgPair<0> {
  typedef MsgBar type;
  enum { id = MSG_BAR };
};

template<typename T, typename U, MsgId V, class W> struct TypeSelect {
  static const MsgId id = W::id;
};

template<typename T, MsgId V, class W> struct TypeSelect<T, T, V, W> {
  static const MsgId id = V;
};

// completely static mapping from message type to message id
template<typename Msg, int n> struct TypeToId {
  typedef typename MsgPair<n>::type t;
  static const MsgId i1 = (MsgId) MsgPair<n>::id;
  static const MsgId id = TypeSelect<Msg, t, i1, class TypeToId<Msg, n + 1> >::id;
};

// static function which unrolls series of ifs to match against given message id
// if match is found FUNC<msg>::Apply() is called 
// otherwise nothing happens
template<template<class Msg> class FUNC, int n> struct IdToType {
  static inline void EXEC(MsgId msgId) {
    if (msgId == (MsgId) MsgPair<n>::id)
      return FUNC<typename MsgPair<n>::type>::Apply();
    return IdToType<FUNC, n + 1>::EXEC(msgId); 
  }
};

// recursion end
template<template<class Msg> class FUNC> struct IdToType <FUNC, 2> {
  static inline void EXEC(MsgId msgId) {};
};

template <class Msg> struct TypeFunctor {
  static void Apply() {
    Msg msg;
    PrintMsg(msg);
  }
};

int main() {
  MsgId msgId; 

  // definition of pairs
  msgId = (MsgId) MsgPair<0>::id;
  std::cout << "MsgPair 0: " << msgId << std::endl;

  msgId = (MsgId) MsgPair<1>::id;
  std::cout << "MsgPair 1: " << msgId << std::endl;

  // this statically sets msgId to MSG_BAR
  msgId = (MsgId) TypeToId<MsgBar, 0>::id;
  std::cout << "TypeToId MsgBar: " << msgId << std::endl;

  // this statically sets msgId to MSG_FOO
  msgId = (MsgId) TypeToId<MsgFoo, 0>::id;
  std::cout << "TypeToId MsgFoo: " << msgId << std::endl;

  // this calls PrintMsg(MsgBar) 
  msgId = MSG_BAR;
  IdToType<TypeFunctor, 0>::EXEC(msgId);

  // this calls PrintMsg(MsgFoo) 
  msgId = MSG_FOO;
  IdToType<TypeFunctor, 0>::EXEC(msgId);

  // this does nothing
  msgId = MSG_BAZ;
  IdToType<TypeFunctor, 0>::EXEC(msgId);
}
